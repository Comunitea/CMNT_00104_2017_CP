# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    scale = fields.Many2one('port.scale', required=True)

    def impute_fault(self):
        new_line_vals = {
            'product_id': self.env.ref('port_scale_sale.product_fault').id,
            'product_uom_qty': 1,
            'price_unit': 0.0,
            'order_id': self.id,
            'product_uom': False,
            'sequence': 100
        }
        new_line = self.env['sale.order.line']
        specs = new_line._onchange_spec()
        onchange_result = new_line.onchange(
            new_line_vals, ['product_id'], specs)
        value = onchange_result.get('value', {})
        for name, val in value.iteritems():
            if isinstance(val, tuple):
                value[name] = val[0]
        new_line_vals.update(value)
        new_line_vals['price_unit'] = self.amount_untaxed
        new_line = self.env['sale.order.line'].create(new_line_vals)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['scale'] = self.scale.id
        return res
