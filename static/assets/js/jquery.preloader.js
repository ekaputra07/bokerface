// Author: Pasek <pasek@egomedia-bali.com>
// File: jquery.preloader.js
// Description: JQuery plugin for image preloader
// Usage: $('.some-element').preloadImage('/images/test.jpg');

(function($){

    $.fn.preloadImage = function(src){
    var that = this;

    init = function(){
	    var img = new Image();
	    $(img).load(function () {
		    $(this).hide();
		    that.append(this).removeClass('loading');
		    $(this).fadeIn();
	    }).attr('src', src);
    };

    init();

    return this;
    };
    
})(jQuery);
 
