# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class Ship(models.Model):

    _name = 'ship'

    name = fields.Char(required=True)
    consignatario = fields.Char()
    flag = fields.Char()
    imo = fields.Char('IMO')
    mmsi = fields.Char('MMSI')
    callsign = fields.Char()
    scales = fields.One2many('port.scale', 'ship')
    scales_count = fields.Integer(compute='_get_scales_count')

    @api.depends('scales')
    def _get_scales_count(self):
        for ship in self:
            ship.scales_count = len(ship.scales)

    def open_ship_scales(self):
        action = self.env.ref('port_scale.port_scale_action')
        result = action.read()[0]
        result['domain'] = [('ship', 'in', self.ids)]
        return result
