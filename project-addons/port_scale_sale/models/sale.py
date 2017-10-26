# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    scale = fields.Many2one('port.scale', required=False)
    ship = fields.Many2one('ship')
    input_request_date = fields.Datetime(related="scale.input_request_date")
    scale_state = fields.Selection(related="scale.state", readonly=True)
    anchoring_request_date = fields.\
        Datetime(related="scale.anchoring_request_date")
    departure_request_date = fields.\
        Datetime(related="scale.departure_request_date")
    coast_pilot = fields.Many2one('res.users')
    operation_start_time = fields.Datetime()
    operation_end_time = fields.Datetime()
    operation = fields.Selection(
        (('D', 'disembarkation'),
         ('E', 'embarkation'),
         ('T', 'transfer'),
         ('R', 'scraps')), related="scale.operation", readonly=True)
    type = fields.Selection(
        (('out', 'Out'),
         ('move', 'Move'),
         ('in', 'In')))
    tugs_in = fields.Many2many('port.tug', related='scale.tugs_in')
    tugs_out = fields.Many2many('port.tug', related='scale.tugs_out')
    tugs_move = fields.Many2many('port.tug', related='scale.tugs_move')

    def _impute(self, product_id, percent):
        new_line_vals = {
            'product_id': product_id,
            'product_uom_qty': 1,
            'price_unit': 0.0,
            'order_id': self.id,
            'product_uom': False,
            'sequence': 100,
            'zone': self.zone
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
        new_line_vals['price_unit'] = self.amount_untaxed * percent
        new_line = self.env['sale.order.line'].create(new_line_vals)

    def impute_fault(self):
        self._impute(self.env.ref('port_scale_sale.product_fault').id, 1)


    def desembarque_ria(self):
        self._impute(self.env.ref('port_scale_sale.product_desembarque_ria').id, 0.5)

    def boat_towing(self):
        new_line_vals = {
            'product_id': self.env.ref('port_scale_sale.product_boat_towing').id,
            'product_uom_qty': 1,
            'price_unit': 0.0,
            'order_id': self.id,
            'product_uom': False,
            'sequence': 100,
            'zone': self.zone
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
        new_line = self.env['sale.order.line'].create(new_line_vals)

    @api.multi
    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        if self._context.get('group_invoices', False) == 'ship':
            vals['ship'] = self.ship.id
        return vals

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        grouped = True
        if self._context.get('group_invoices', False) == 'ship':
            inv_obj = self.env['account.invoice']
            precision = self.env['decimal.precision'].precision_get(
                'Product Unit of Measure')
            invoices = {}
            references = {}
            for order in self:
                group_key = (order.partner_invoice_id.id,
                             order.scale.ship.id,
                             order.currency_id.id,
                             order.fiscal_position_id.id)
                for line in order.order_line.sorted(
                        key=lambda l: l.qty_to_invoice < 0):
                    if float_is_zero(line.qty_to_invoice,
                                     precision_digits=precision):
                        continue
                    if group_key not in invoices:
                        inv_data = order._prepare_invoice()
                        invoice = inv_obj.create(inv_data)
                        references[invoice] = order
                        invoices[group_key] = invoice
                    elif group_key in invoices:
                        vals = {}
                        if order.name not in \
                                invoices[group_key].origin.split(', '):
                            vals['origin'] = invoices[group_key].origin + \
                                ', ' + order.name
                        if order.client_order_ref and \
                                order.client_order_ref not in \
                                invoices[group_key].name.split(', '):
                            vals['name'] = invoices[group_key].name + \
                                ', ' + order.client_order_ref
                        invoices[group_key].write(vals)
                    if line.qty_to_invoice > 0:
                        line.invoice_line_create(invoices[group_key].id,
                                                 line.qty_to_invoice)
                    elif line.qty_to_invoice < 0 and final:
                        line.invoice_line_create(invoices[group_key].id,
                                                 line.qty_to_invoice)

                if references.get(invoices.get(group_key)):
                    if order not in references[invoices[group_key]]:
                        references[invoice] = references[invoice] | order

            if not invoices:
                raise UserError(_('There is no invoicable line.'))

            for invoice in invoices.values():
                if not invoice.invoice_line_ids:
                    raise UserError(_('There is no invoicable line.'))
                # If invoice is negative, do a refund invoice instead
                if invoice.amount_untaxed < 0:
                    invoice.type = 'out_refund'
                    for line in invoice.invoice_line_ids:
                        line.quantity = -line.quantity
                # Use additional field helper function (for account extensions)
                for line in invoice.invoice_line_ids:
                    line._set_additional_fields(invoice)
                # Necessary to force computation of taxes. In account_invoice,
                # they are triggered
                # by onchanges, which are not triggered when doing a create.
                invoice.compute_taxes()
                invoice.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': invoice, 'origin': references[invoice]},
                    subtype_id=self.env.ref('mail.mt_note').id)
            return [inv.id for inv in invoices.values()]
        elif self._context.get('group_invoices', False) == 'partner':
            grouped = False
        return super(SaleOrder, self).action_invoice_create(grouped, final)


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['name'] += ' %s' % self.order_id.ship.name
        return res
