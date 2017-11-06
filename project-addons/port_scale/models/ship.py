# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Ship(models.Model):

    _name = 'ship'

    name = fields.Char(required=True)
    country = fields.Many2one('res.country')
    imo = fields.Char('IMO')
    mmsi = fields.Char('MMSI')
    callsign = fields.Char()
    scales = fields.One2many('port.scale', 'ship')
    scales_count = fields.Integer(compute='_get_scales_count')
    gt = fields.Float("GT")
    attachment_count = fields.Integer(
        'Attachments', compute='_compute_attachment_count',
        search='_search_attachment_count')

    @api.depends('scales')
    def _get_scales_count(self):
        for ship in self:
            ship.scales_count = len(ship.scales)

    def open_ship_scales(self):
        action = self.env.ref('port_scale.port_scale_action')
        result = action.read()[0]
        result['domain'] = [('ship', 'in', self.ids)]
        return result

    def _search_attachment_count(self, operator, operand):
        if operand in (None, False):
            operand = 0
        self.env.cr.execute("""
SELECT sp.id as id
FROM ir_attachment ia RIGHT OUTER JOIN
     ship sp ON ia.res_id=sp.id AND ia.res_model='ship'
GROUP BY sp.id
HAVING count(ia.id) %s %s;
        """ % (operator, operand))
        ship_ids = [x[0] for x in self.env.cr.fetchall()]
        return [('id', 'in', ship_ids)]

    def _compute_attachment_count(self):
        for ship in self:
            ship.attachment_count = len(self.env['ir.attachment'].search(
                [('res_model', '=', 'ship'), ('res_id', '=', ship.id)]))
