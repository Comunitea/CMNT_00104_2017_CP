# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    group_invoices = fields.Selection(
        (('partner', 'By partner'), ('ship', 'By ship')))

    @api.multi
    def create_invoices(self):
        return super(
            SaleAdvancePaymentInv,
            self.with_context(group_invoices=self.group_invoices)
        ).create_invoices()
