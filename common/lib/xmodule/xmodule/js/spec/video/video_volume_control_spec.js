(function() {
  describe('VideoVolumeControl', function() {
    var state, videoControl, videoVolumeControl, oldOTBD;

    function initialize() {
      loadFixtures('video_all.html');
      state = new Video('#example');
      videoControl = state.videoControl;
      videoVolumeControl = state.videoVolumeControl;
    }

    beforeEach(function() {
      oldOTBD = window.onTouchBasedDevice;
      window.onTouchBasedDevice = jasmine.createSpy('onTouchBasedDevice').andReturn(false);
    });

    afterEach(function() {
        $('source').remove();
        window.onTouchBasedDevice = oldOTBD;
    });

    describe('constructor', function() {
      beforeEach(function() {
        spyOn($.fn, 'slider').andCallThrough();
        initialize();

        this.addMatchers({
          toBeInRange: function(min, max) {
            return min <= this.actual && this.actual <= max;
          },

          toBeInArray: function(arr) {
            return $.inArray(this.actual, arr) === -1 ? false : true;
          }
        });
      });

      it('initialize currentVolume to 100', function() {
        expect(state.videoVolumeControl.currentVolume).toEqual(1);
      });

      it('render the volume control', function() {
        expect(videoControl.secondaryControlsEl.html()).toContain("<div class=\"volume\">\n");
      });

      it('create the slider', function() {
        expect($.fn.slider).toHaveBeenCalledWith({
          orientation: "vertical",
          range: "min",
          min: 0,
          max: 100,
          value: videoVolumeControl.currentVolume,
          change: videoVolumeControl.onChange,
          slide: videoVolumeControl.onChange
        });
      });

      it('add ARIA attributes to slider handle', function () {
        var sliderHandle = $('div.volume-slider>a.ui-slider-handle'),
        arr = ['muted', 'very low', 'low', 'average', 'loud', 'very loud',
               'maximum'];
        expect(sliderHandle).toHaveAttr('role', 'slider');
        expect(sliderHandle).toHaveAttr('title', 'volume');  
        expect(sliderHandle).toHaveAttr('aria-disabled', 'false');
        expect(sliderHandle).toHaveAttr( 'aria-valuemin', '0');
        expect(sliderHandle).toHaveAttr( 'aria-valuemax', '100');
        expect(sliderHandle.attr('aria-valuenow')).toBeInRange(0, 100);
        expect(sliderHandle.attr('aria-valuetext')).toBeInArray(arr);
      });
 
      it('add ARIA attributes to volume control', function () {
        var volumeControl = $('div.volume>a');
        expect(volumeControl).toHaveAttr('role', 'button');
        expect(volumeControl).toHaveAttr('title', 'Volume');
        expect(volumeControl).toHaveAttr('aria-disabled', 'false');
      });

      it('bind the volume control', function() {
        expect($('.volume>a')).toHandleWith('click', videoVolumeControl.toggleMute);
        expect($('.volume')).not.toHaveClass('open');
        $('.volume').mouseenter();
        expect($('.volume')).toHaveClass('open');
        $('.volume').mouseleave();
        expect($('.volume')).not.toHaveClass('open');
      });
    });

    describe('onChange', function() {
      beforeEach(function() {
        initialize();
      });

      describe('when the new volume is more than 0', function() {
        beforeEach(function() {
          videoVolumeControl.onChange(void 0, {
            value: 60
          });
        });

        it('set the player volume', function() {
          expect(videoVolumeControl.currentVolume).toEqual(60);
        });

        it('remote muted class', function() {
          expect($('.volume')).not.toHaveClass('muted');
        });
      });

      describe('when the new volume is 0', function() {
        beforeEach(function() {
          videoVolumeControl.onChange(void 0, {
            value: 0
          });
        });

        it('set the player volume', function() {
          expect(videoVolumeControl.currentVolume).toEqual(0);
        });

        it('add muted class', function() {
          expect($('.volume')).toHaveClass('muted');
        });
      });
    });

    describe('toggleMute', function() {
      beforeEach(function() {
        initialize();
      });

      describe('when the current volume is more than 0', function() {
        beforeEach(function() {
          videoVolumeControl.currentVolume = 60;
          videoVolumeControl.buttonEl.trigger('click');
        });

        it('save the previous volume', function() {
          expect(videoVolumeControl.previousVolume).toEqual(60);
        });

        it('set the player volume', function() {
          expect(videoVolumeControl.currentVolume).toEqual(0);
        });
      });

      describe('when the current volume is 0', function() {
        beforeEach(function() {
          videoVolumeControl.currentVolume = 0;
          videoVolumeControl.previousVolume = 60;
          videoVolumeControl.buttonEl.trigger('click');
        });

        it('set the player volume to previous volume', function() {
          expect(videoVolumeControl.currentVolume).toEqual(60);
        });
      });
    });
  });

}).call(this);
