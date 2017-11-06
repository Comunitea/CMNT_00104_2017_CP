# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    paydays = fields.Integer(compute='_compute_paydays', store=True)

    @api.depends('date_invoice', 'payment_move_line_ids.date')
    def _compute_paydays(self):
        for invoice in self:
            invoice_date = fields.Date.from_string(invoice.date_invoice)
            payment_date = False
            for payment in invoice.payment_move_line_ids:
                pdate = fields.Date.from_string(payment.date)
                if not payment_date or payment_date < pdate:
                    payment_date = pdate
            if invoice_date and payment_date:
                invoice.paydays = (payment_date - invoice_date).days
            else:
                invoice.paydays = 0
