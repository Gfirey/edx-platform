$(document).ready(function () {
  // define variables for code legibility
  var dropdownMenuToggle = $('a.dropdown');
  var dropdownMenu = $('ul.dropdown-menu');
  var menuItems = dropdownMenu.children().children('a');
  
  // bind menu toggle click for later use
  dropdownMenuToggle.toggle(function() {
    dropdownMenu.addClass("expanded").children().children('a').first().focus();
    dropdownMenuToggle.addClass("active").attr("aria-expanded", "true");
  }, function() {
    dropdownMenu.removeClass("expanded");
    dropdownMenuToggle.removeClass("active").attr("aria-expanded", "false").focus();
  });
  
  //catch keypresses when focused on dropdownMenuToggle and dropdownMenu
  dropdownMenuToggle.on('keydown', function(event){ catchKeyPress($(this), event); })
  dropdownMenu.on('keydown', function(event){ catchKeyPress($(this), event); })
  
  function catchKeyPress(object, event) {
    // get currently focused item
    var focusedItem = jQuery(':focus');

    // get the number of focusable items
    var numberOfMenuItems = menuItems.length

    // get the index of the currently focused item
    var focusedItemIndex = menuItems.index(focusedItem);
    
    // var to store next focused item index
    var itemToFocusIndex;
    
    // if space key pressed
	if ( event.which == 32) {
      dropdownMenuToggle.click();
      event.preventDefault();
    }
    
    // if escape key pressed and menu open
	if ( event.which == 27 && (object.hasClass('expanded') || object.hasClass('active'))) {
      dropdownMenuToggle.click();
      event.preventDefault();
    }
    
    // if up arrow key pressed
	if ( event.which == 38) {
      // if first item go to last
      if (focusedItemIndex === 0) {
        menuItems.last().focus();
      } else {
        itemToFocusIndex = focusedItemIndex - 1;
        menuItems.get(itemToFocusIndex).focus();
      }
      event.preventDefault();
    }
    
    // if down arrow key pressed
	if ( event.which == 40) {
      // if last item go to first
      if (focusedItemIndex == numberOfMenuItems - 1) {
        menuItems.first().focus();
      } else {
        itemToFocusIndex = focusedItemIndex + 1;
        menuItems.get(itemToFocusIndex).focus();
      }
      event.preventDefault();
    }
  }
});