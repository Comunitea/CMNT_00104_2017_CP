# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions, _


class PortScaleCreateOrder(models.TransientModel):

    _name = 'port.scale.create.order'

    @api.multi
    def create_order(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}
