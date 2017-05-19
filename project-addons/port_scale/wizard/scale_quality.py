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
         ))
    scale_id = fields.Many2one('port.scale', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(ScaleQualityWizard, self).default_get(fields)
        res['scale_id'] = self.env['port.scale'].browse(
            self._context.get('active_id', False)).id
        return res

    @api.multi
    def confirm_0(self):
        return self.confirm(0)

    @api.multi
    def confirm_1(self):
        return self.confirm(1)

    @api.multi
    def confirm_2(self):
        return self.confirm(2)

    @api.multi
    def confirm(self, satisfaction):
        self.scale_id.quality_signature = self.signature
        self.scale_id.quality_service_satisfaction = satisfaction
        return {'type': 'ir.actions.act_window_close'}
