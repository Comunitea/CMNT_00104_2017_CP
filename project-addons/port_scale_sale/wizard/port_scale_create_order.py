# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, exceptions, _


class PortScaleCreateOrder(models.TransientModel):

    _name = 'port.scale.create.order'

    scale = fields.Many2one('port.scale')
    ship = fields.Many2one('ship', related='scale.ship', required=True)
    dock = fields.Many2one('port.dock', related='scale.dock')
    input_request_date = fields.Datetime(related="scale.input_request_date")
    scale_state = fields.Selection(related="scale.state", readonly=True)
    anchoring_request_date = fields.\
        Datetime(related="scale.anchoring_request_date")
    departure_request_date = fields.\
        Datetime(related="scale.departure_request_date")
    operation_start_time = fields.Datetime()
    operation_end_time = fields.Datetime()
    country = fields.Many2one('res.country',
                              related='scale.ship.country', required=True)
    gt = fields.Float(related='scale.gt', required=True)
    partner_id = fields.Many2one('res.partner',
                                 related='scale.partner_id',
                                 required=True)
    partner_name = fields.Char(related='scale.partner_name', readonly=True)
    tugs_in = fields.Many2many('port.tug', related='scale.tugs_in')
    tugs_out = fields.Many2many('port.tug', related='scale.tugs_out')
    tugs_move = fields.Many2many('port.tug', related='scale.tugs_move')
    user_id = fields.Many2one('res.users', 'Coast pilot', required=True)
    pricelist = fields.Many2one('product.pricelist', required=True)
    fiscal_position = fields.Many2one('account.fiscal.position', default=lambda self: self.env.ref('l10n_es.1_fp_extra'))
    zone = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C')], 'Zone',
                            default='A', required=True)
    type = fields.Selection(
        (('entrada', 'Entrada'),
         ('movimiento', 'Movimiento'),
         ('salida', 'Salida'),
         ('compensacion', 'Compensación')
         ), required=True)
    reten = fields.Boolean(related='scale.reten')
    reten_subalterno = fields.Boolean(related='scale.reten_subalterno')


    """"@api.onchange('type')
    def onchange_type(self):
        if self.type == 'docking':
            self.operation_start_time = self.scale.docking_start_time
            self.operation_end_time = self.scale.docking_end_time
        if self.type == 'undocking':
            self.operation_start_time = self.scale.undocking_start_time
            self.operation_end_time = self.scale.undocking_end_time
        if self.type == 'move':
            self.operation_start_time = self.scale.change_docking_start_time
            self.operation_end_time = self.scale.change_docking_end_time
        if self.type == 'in':
            self.operation_start_time = self.scale.anchor_start_time
            self.operation_end_time = self.scale.anchor_end_time"""

    @api.model
    def default_get(self, fields):
        res = super(PortScaleCreateOrder, self).default_get(fields)
        scale = self.env['port.scale'].browse(
            self._context.get('active_id', False))
        res['scale'] = scale.id
        res['type'] = self._context.get('sale_type', False)
        res['operation_start_time'] = self._context.get('start_time', False)
        res['operation_end_time'] = self._context.get('end_time', False)
        res['user_id'] = self.env.user.id
        partner = self.env['res.partner'].search(
            [('name', '=', scale.partner_name)])
        if partner:
            scale.partner_id = partner.id
        return res

    @api.multi
    def create_order(self):
        if self.operation_start_time and self.operation_end_time and \
                self.operation_start_time > self.operation_end_time:
            raise exceptions.UserError(
                _('The operation start time must be earlier than the \
operation end time'))
        order_vals = {
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist.id,
            'scale': self.scale.id,
            'ship': self.scale.ship.id,
            'coast_pilot': self.user_id.id,
            'fiscal_position_id': self.fiscal_position.id,
            'type': self.type,
            'operation_start_time': self.operation_start_time,
            'operation_end_time': self.operation_end_time,
            'zone': self.zone
        }

        #Rellenamos el campo 'remolcadores' en función de la operación
        if self.type == 'in':
            order_vals['tugs'] = [(6, 0, self.tugs_in.ids)]
        elif self.type == 'move':
            order_vals['tugs'] = [(6, 0, self.tugs_move.ids)]
        elif self.type == 'out':
            order_vals['tugs'] = [(6, 0, self.tugs_out.ids)]

        if self.scale_state == 'input':
            order_vals['request_date'] = self.scale.input_request_date
            scale_request_date = self.scale.input_request_date
        elif self.scale_state == 'anchoring':
            order_vals['request_date'] = self.scale.anchoring_request_date
            scale_request_date = self.scale.anchoring_request_date
        elif self.scale_state == 'departure':
            order_vals['request_date'] = self.scale.departure_request_date
            scale_request_date = self.scale.departure_request_date

        new_order = self.env['sale.order'].create(order_vals)
        if self.type:
            TYPES_DICT = {
                'entrada': 'in',
                'movimiento': 'move',
                'salida': 'out',
                'compensacion': 'compensacion'
            }
            prods = [self.env.ref('port_scale_sale.product_%s' % TYPES_DICT[self.type])]
            if self.type == 'in':
                prods.append(self.env.ref('port_scale_sale.product_docking'))
            elif self.type == 'move':
                prods.append(self.env.ref('port_scale_sale.product_docking'))
                prods.append(self.env.ref('port_scale_sale.product_undocking'))
            elif self.type == 'out':
                prods.append(self.env.ref('port_scale_sale.product_undocking'))
            for line_prod in prods:
                new_line_vals = {
                    'product_id': line_prod.id,
                    'product_uom_qty': 1,
                    'order_id': new_order.id,
                    'zone': self.zone
                }
                new_line = self.env['sale.order.line'].new(new_line_vals)
                new_line.product_id_change()
                new_line.gt_zone_change()
                line_vals = new_line._convert_to_write(new_line._cache)
                iva_21_account_tax = self.env['account.tax'].search([('name','=','S_IVA21')])
                if iva_21_account_tax:
                    iva_21_account_tax_id = iva_21_account_tax.id
                #line_vals.update({'tax_id': self.fiscal_position.id == self.env.ref('l10n_es.1_fp_nacional').id and [(6, 0, [self.env.ref('l10n_es.account_tax_template_s_iva21s').id])] or []})
                line_vals.update({'tax_id': self.fiscal_position.id == self.env.ref('l10n_es.1_fp_nacional').id and [
                    (6, 0, [iva_21_account_tax_id])] or []})
                new_line = self.env['sale.order.line'].create(line_vals)
        new_order.action_confirm()
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = "[('id', '=', " + str(new_order.id) + ")]"

        #Actualizo el campo de la escala
        scale_write_vals = {'request_date': scale_request_date}

        if self.type == 'move':
            scale_write_vals.update({'change_docking_start_time': self.operation_start_time})
            scale_write_vals.update({'change_docking_end_time': self.operation_end_time})
        elif self.type == 'in':
            if self.scale.anchor_start_time:
                scale_write_vals.update({'anchor_start_time': self.operation_start_time})
                scale_write_vals.update({'anchor_end_time': self.operation_end_time})
            else:
                scale_write_vals.update({'docking_start_time': self.operation_start_time})
                scale_write_vals.update({'docking_end_time': self.operation_end_time})
        elif self.type == 'out':
            scale_write_vals.update({'undocking_start_time': self.operation_start_time})
            scale_write_vals.update({'undocking_end_time': self.operation_end_time})

        #print '*********SELF.TYPE: %s' % (self.type)
        #print '*********SCALE WRITE VALS: %s'%(scale_write_vals)
        self.scale.write(scale_write_vals)



        if self.env.context.get("next_state", False):
            eval("self.scale." + self.env.context["next_state"],
                 {'self': self})
        return action
