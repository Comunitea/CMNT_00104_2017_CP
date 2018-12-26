odoo.define('port_scale.PortelMenu', function(require) {
"use strict";

var Model = require('web.Model');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');

var PortelMenu = Widget.extend({
    template: 'PortelMenu',

    start: function() {
        var self = this;
        var scale_facade = new Model('port.scale');
        this.$el.click(function(e){
            scale_facade.call('import_api_data')
            var window_action = {
                name: 'Importaciones de Portel',
                type: 'ir.actions.act_window',
                res_model: 'port.scale.history',
                view_mode: 'list',
                view_type: 'list',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',
            }
            // self.do_action accepts the action parameter and opens the new view
            self.do_action(window_action);
        });
    },
 });
SystrayMenu.Items.push(PortelMenu);
});