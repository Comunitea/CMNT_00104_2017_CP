odoo.define('port_scale.TideMenu', function(require) {
"use strict";

var Model = require('web.Model');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');

var TideMenu = Widget.extend({
    template: 'TideMenu',

    start: function() {
        var self = this;
        var tide = new Model("port.tide");
        this.$el.click(function(e){
            var tides_list = '';
            tide.call("get_today_tides").then(function(result) {
            _.each(result, function(tide_tuple){
                tides_list += '<li><div class="row"><div class="col-xs-4"><span>' + tide_tuple[0] + '</span></div><div class="col-xs-4"><span>' + tide_tuple[1] + '</span></div><div class="col-xs-4"><span>' + tide_tuple[2] + '</span></div></div></li>'
            });
            self.$('.dropdown-menu').html(tides_list);
        });
        });

        return this._super();
    },
});

SystrayMenu.Items.push(TideMenu);

});
