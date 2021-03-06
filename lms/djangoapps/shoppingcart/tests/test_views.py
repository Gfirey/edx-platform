"""
Tests for Shopping Cart views
"""
from urlparse import urlparse

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.exceptions import ItemNotFoundError
from courseware.tests.tests import TEST_DATA_MONGO_MODULESTORE
from shoppingcart.views import add_course_to_cart
from shoppingcart.models import Order, OrderItem, CertificateItem, InvalidCartItem, PaidCourseRegistration
from student.tests.factories import UserFactory
from student.models import CourseEnrollment
from course_modes.models import CourseMode
from ..exceptions import PurchasedCallbackException
from mitxmako.shortcuts import render_to_response
from shoppingcart.processors import render_purchase_form_html, process_postpay_callback
from mock import patch, Mock


def mock_render_purchase_form_html(*args, **kwargs):
    return render_purchase_form_html(*args, **kwargs)

form_mock = Mock(side_effect=mock_render_purchase_form_html)

def mock_render_to_response(*args, **kwargs):
    return render_to_response(*args, **kwargs)

render_mock = Mock(side_effect=mock_render_to_response)

postpay_mock = Mock()


@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class ShoppingCartViewsTests(ModuleStoreTestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.user.set_password('password')
        self.user.save()
        self.course_id = "MITx/999/Robot_Super_Course"
        self.cost = 40
        self.course = CourseFactory.create(org='MITx', number='999', display_name='Robot Super Course')
        self.course_mode = CourseMode(course_id=self.course_id,
                                      mode_slug="honor",
                                      mode_display_name="honor cert",
                                      min_price=self.cost)
        self.course_mode.save()
        self.verified_course_id = 'org/test/Test_Course'
        CourseFactory.create(org='org', number='test', run='course1', display_name='Test Course')
        self.cart = Order.get_cart_for_user(self.user)

    def login_user(self):
        self.client.login(username=self.user.username, password="password")

    def test_add_course_to_cart_anon(self):
        resp = self.client.post(reverse('shoppingcart.views.add_course_to_cart', args=[self.course_id]))
        self.assertEqual(resp.status_code, 403)

    def test_add_course_to_cart_already_in_cart(self):
        PaidCourseRegistration.add_to_order(self.cart, self.course_id)
        self.login_user()
        resp = self.client.post(reverse('shoppingcart.views.add_course_to_cart', args=[self.course_id]))
        self.assertEqual(resp.status_code, 400)
        self.assertIn(_('The course {0} is already in your cart.'.format(self.course_id)), resp.content)

    def test_add_course_to_cart_already_registered(self):
        CourseEnrollment.enroll(self.user, self.course_id)
        self.login_user()
        resp = self.client.post(reverse('shoppingcart.views.add_course_to_cart', args=[self.course_id]))
        self.assertEqual(resp.status_code, 400)
        self.assertIn(_('You are already registered in course {0}.'.format(self.course_id)), resp.content)

    def test_add_nonexistent_course_to_cart(self):
        self.login_user()
        resp = self.client.post(reverse('shoppingcart.views.add_course_to_cart', args=['non/existent/course']))
        self.assertEqual(resp.status_code, 404)
        self.assertIn(_("The course you requested does not exist."), resp.content)

    def test_add_course_to_cart_success(self):
        self.login_user()
        resp = self.client.post(reverse('shoppingcart.views.add_course_to_cart', args=[self.course_id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(PaidCourseRegistration.contained_in_order(self.cart, self.course_id))


    @patch('shoppingcart.views.render_purchase_form_html', form_mock)
    @patch('shoppingcart.views.render_to_response', render_mock)
    def test_show_cart(self):
        self.login_user()
        reg_item = PaidCourseRegistration.add_to_order(self.cart, self.course_id)
        cert_item = CertificateItem.add_to_order(self.cart, self.verified_course_id, self.cost, 'honor')
        resp = self.client.get(reverse('shoppingcart.views.show_cart', args=[]))
        self.assertEqual(resp.status_code, 200)

        ((purchase_form_arg_cart,), _) = form_mock.call_args
        purchase_form_arg_cart_items = purchase_form_arg_cart.orderitem_set.all().select_subclasses()
        self.assertIn(reg_item, purchase_form_arg_cart_items)
        self.assertIn(cert_item, purchase_form_arg_cart_items)
        self.assertEqual(len(purchase_form_arg_cart_items), 2)

        ((template, context), _) = render_mock.call_args
        self.assertEqual(template, 'shoppingcart/list.html')
        self.assertEqual(len(context['shoppingcart_items']), 2)
        self.assertEqual(context['amount'], 80)
        self.assertIn("80.00", context['form_html'])

    def test_clear_cart(self):
        self.login_user()
        PaidCourseRegistration.add_to_order(self.cart, self.course_id)
        CertificateItem.add_to_order(self.cart, self.verified_course_id, self.cost, 'honor')
        self.assertEquals(self.cart.orderitem_set.count(), 2)
        resp = self.client.post(reverse('shoppingcart.views.clear_cart', args=[]))
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(self.cart.orderitem_set.count(), 0)

    @patch('shoppingcart.views.log.exception')
    def test_remove_item(self, exception_log):
        self.login_user()
        reg_item = PaidCourseRegistration.add_to_order(self.cart, self.course_id)
        cert_item = CertificateItem.add_to_order(self.cart, self.verified_course_id, self.cost, 'honor')
        self.assertEquals(self.cart.orderitem_set.count(), 2)
        resp = self.client.post(reverse('shoppingcart.views.remove_item', args=[]),
                                {'id': reg_item.id})
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(self.cart.orderitem_set.count(), 1)
        self.assertNotIn(reg_item, self.cart.orderitem_set.all().select_subclasses())

        self.cart.purchase()
        resp2 = self.client.post(reverse('shoppingcart.views.remove_item', args=[]),
                                 {'id': cert_item.id})
        self.assertEqual(resp2.status_code, 200)
        exception_log.assert_called_with(
            'Cannot remove cart OrderItem id={0}. DoesNotExist or item is already purchased'.format(cert_item.id))

        resp3 = self.client.post(reverse('shoppingcart.views.remove_item', args=[]),
                                 {'id': -1})
        self.assertEqual(resp3.status_code, 200)
        exception_log.assert_called_with(
            'Cannot remove cart OrderItem id={0}. DoesNotExist or item is already purchased'.format(-1))

    @patch('shoppingcart.views.process_postpay_callback', postpay_mock)
    def test_postpay_callback_success(self):
        postpay_mock.return_value = {'success': True, 'order': self.cart}
        self.login_user()
        resp = self.client.post(reverse('shoppingcart.views.postpay_callback', args=[]))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp.__getitem__('location')).path,
                         reverse('shoppingcart.views.show_receipt', args=[self.cart.id]))

    @patch('shoppingcart.views.process_postpay_callback', postpay_mock)
    @patch('shoppingcart.views.render_to_response', render_mock)
    def test_postpay_callback_failure(self):
        postpay_mock.return_value = {'success': False, 'order': self.cart, 'error_html': 'ERROR_TEST!!!'}
        self.login_user()
        resp = self.client.post(reverse('shoppingcart.views.postpay_callback', args=[]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('ERROR_TEST!!!', resp.content)

        ((template, context), _) = render_mock.call_args
        self.assertEqual(template, 'shoppingcart/error.html')
        self.assertEqual(context['order'], self.cart)
        self.assertEqual(context['error_html'], 'ERROR_TEST!!!')

    def test_show_receipt_404s(self):
        PaidCourseRegistration.add_to_order(self.cart, self.course_id)
        CertificateItem.add_to_order(self.cart, self.verified_course_id, self.cost, 'honor')
        self.cart.purchase()

        user2 = UserFactory.create()
        cart2 = Order.get_cart_for_user(user2)
        PaidCourseRegistration.add_to_order(cart2, self.course_id)
        cart2.purchase()

        self.login_user()
        resp = self.client.get(reverse('shoppingcart.views.show_receipt', args=[cart2.id]))
        self.assertEqual(resp.status_code, 404)

        resp2 = self.client.get(reverse('shoppingcart.views.show_receipt', args=[1000]))
        self.assertEqual(resp2.status_code, 404)

    @patch('shoppingcart.views.render_to_response', render_mock)
    def test_show_receipt_success(self):
        reg_item = PaidCourseRegistration.add_to_order(self.cart, self.course_id)
        cert_item = CertificateItem.add_to_order(self.cart, self.verified_course_id, self.cost, 'honor')
        self.cart.purchase(first='FirstNameTesting123', street1='StreetTesting123')

        self.login_user()
        resp = self.client.get(reverse('shoppingcart.views.show_receipt', args=[self.cart.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('FirstNameTesting123', resp.content)
        self.assertIn('80.00', resp.content)

        ((template, context), _) = render_mock.call_args
        self.assertEqual(template, 'shoppingcart/receipt.html')
        self.assertEqual(context['order'], self.cart)
        self.assertIn(reg_item, context['order_items'])
        self.assertIn(cert_item, context['order_items'])
        self.assertFalse(context['any_refunds'])

    @patch('shoppingcart.views.render_to_response', render_mock)
    def test_show_receipt_success_refund(self):
        reg_item = PaidCourseRegistration.add_to_order(self.cart, self.course_id)
        cert_item = CertificateItem.add_to_order(self.cart, self.verified_course_id, self.cost, 'honor')
        self.cart.purchase(first='FirstNameTesting123', street1='StreetTesting123')
        cert_item.status = "refunded"
        cert_item.save()
        self.assertEqual(self.cart.total_cost, 40)
        self.login_user()
        resp = self.client.get(reverse('shoppingcart.views.show_receipt', args=[self.cart.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('40.00', resp.content)

        ((template, context), _tmp) = render_mock.call_args
        self.assertEqual(template, 'shoppingcart/receipt.html')
        self.assertEqual(context['order'], self.cart)
        self.assertIn(reg_item, context['order_items'])
        self.assertIn(cert_item, context['order_items'])
        self.assertTrue(context['any_refunds'])

    @patch('shoppingcart.views.render_to_response', render_mock)
    def test_show_receipt_success_custom_receipt_page(self):
        cert_item = CertificateItem.add_to_order(self.cart, self.course_id, self.cost, 'honor')
        self.cart.purchase()
        self.login_user()
        receipt_url = reverse('shoppingcart.views.show_receipt', args=[self.cart.id])
        resp = self.client.get(receipt_url)
        self.assertEqual(resp.status_code, 200)
        ((template, _context), _tmp) = render_mock.call_args
        self.assertEqual(template, cert_item.single_item_receipt_template)
