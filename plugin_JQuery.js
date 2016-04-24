(function($) {
    var methods = {
        init: function(options) {
			this.settings = $.extend( {}, this.defaults, options );
            return this;
        },
        option: function(key, value) {
            var ret = this;
            this.each(function() {
                if (value == undefined)
                    ret = this.setting[key];
                else
                    this.setting[key] = value;
            });
            return ret;
        }
    };
    $.fn.plugin_JQuery = function(methodOrOptions) {
        if ( methods[methodOrOptions] ) {
            return methods[ methodOrOptions ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof methodOrOptions === 'object' || ! methodOrOptions ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  methodOrOptions + ' does not exist on jQuery.plugin_JQuery' );
        }
    };

    $.fn.plugin_JQuery.defaults = {
        onComplete: function(element, response){},
        onSend: function(element, jqXHR, settings){},
        onError: function(element, jqXHR, textStatus, errorThrown){},
        onSuccess: function (element, data, textStatus, jqXHR) {},
        onProgress: function (element, data) {}
    };


})(jQuery);