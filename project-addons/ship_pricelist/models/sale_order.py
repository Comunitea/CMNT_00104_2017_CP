# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    gt = fields.Integer("GT")
    zone = fields.Selection([('A', 'A'), ('B', 'B')], 'Zona', default = 'A')


    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        self.gt = self.order_id.scale.gt
        result = super(SaleOrderLine, self).product_id_change()
        return result