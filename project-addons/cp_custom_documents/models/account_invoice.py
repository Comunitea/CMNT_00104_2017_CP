# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ui(models.Model):

    _inherit = 'account.invoice'

    sales = fields.One2many('sale.order', compute='_compute_sales')
    ships = fields.One2many('ship', compute='_compute_ships')

    def _compute_sales(self):
        for invoice in self:
            sales = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')
            invoice.sales = sales

    def _compute_ships(self):
        for invoice in self:
            ships = invoice.mapped(
                'invoice_line_ids.sale_line_ids.order_id.scale.ship')
            invoice.ships = ships
