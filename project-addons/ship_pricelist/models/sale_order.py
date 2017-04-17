# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
#TODO REVISAR CON LO QUE SUBA JESUS PARA VER COMO SON LOS CAMPOS ZONE Y GT
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    zone = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C')], 'Zona', default='A')

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    gt = fields.Integer("GT")
    zone = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C')], 'Zona')


    @api.multi
    @api.onchange('gt', 'zone')
    def gt_zone_change(self):

        vals = {}
        product = self.product_id.with_context(
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            )
        self._compute_tax_id()
        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
        self.update(vals)
