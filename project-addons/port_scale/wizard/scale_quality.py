# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from ..models.tug_data import TUG_SELECTOR


class ScaleQualityWizard(models.TransientModel):

    _name = 'scale.quality.wizard'

    signature = fields.Binary()
    service_satisfaction = fields.Selection(
        (('0', '0'),
         ('1', '1'),
         ('2', '2'),
         ('3', '3'),
         ('4', '4'),
         ('5', '5'),
         ))
    scale_id = fields.Many2one('port.scale', readonly=True)
    name = fields.Char('Scale', related='scale_id.name', readonly=True)
    eta = fields.Datetime(related='scale_id.eta', readonly=True)
    ship_name = fields.Char('Name', related='scale_id.ship.name',
                            readonly=True)
    country = fields.Many2one('res.country',
                              related='scale_id.ship.country', readonly=True)
    gt = fields.Integer(related='scale_id.gt', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Agent',
                                 related='scale_id.ship.partner_id',
                                 readonly=True)
    draft = fields.Float(related='scale_id.draft', readonly=True)
    norays = fields.Char(related='scale_id.norays', readonly=True)
    tug_number = fields.Selection(TUG_SELECTOR, related='scale_id.tug_number',
                                readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(ScaleQualityWizard, self).default_get(fields)
        res['scale_id'] = self.env['port.scale'].browse(
            self._context.get('active_id', False)).id
        return res

    @api.multi
    def confirm(self):
        self.scale_id.quality_signature = self.signature
        self.scale_id.quality_service_satisfaction = int(
            self.service_satisfaction)
        return {'type': 'ir.actions.act_window_close'}
