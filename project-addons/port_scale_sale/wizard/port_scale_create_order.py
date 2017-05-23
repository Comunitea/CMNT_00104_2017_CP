# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class PortScaleCreateOrder(models.TransientModel):

    _name = 'port.scale.create.order'

    scale = fields.Many2one('port.scale')
    ship = fields.Many2one('ship', related='scale.ship', required=True)
    operation_start_time = fields.Datetime()
    operation_end_time = fields.Datetime()
    country = fields.Many2one('res.country',
                              related='scale.ship.country', required=True)
    gt = fields.Integer(related='scale.gt', required=True)
    partner_id = fields.Many2one('res.partner',
                                 related='scale.ship.partner_id',
                                 required=True)
    tugs = fields.Many2many('port.tug', related='scale.tugs', required=True)
    user_id = fields.Many2one('res.users', 'Coast pilot', required=True)
    pricelist = fields.Many2one('product.pricelist', required=True)
    fiscal_position = fields.Many2one('account.fiscal.position')
    zone = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C')], 'Zone',
                            default='A', required=True)
    type = fields.Selection(
        (('docking', 'Docking'),
         ('undocking', 'Undocking'),
         ('move', 'Move'),
         ('in', 'In')), required=True)
    reten = fields.Boolean(related='scale.reten')

    @api.onchange('type')
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
            self.operation_end_time = self.scale.anchor_end_time

    @api.model
    def default_get(self, fields):
        res = super(PortScaleCreateOrder, self).default_get(fields)
        res['scale'] = self.env['port.scale'].browse(
            self._context.get('active_id', False)).id
        res['type'] = self._context.get('sale_type', False)
        res['operation_start_time'] = self._context.get('start_time', False)
        res['operation_end_time'] = self._context.get('end_time', False)
        res['user_id'] = self.env.user.id
        return res

    @api.multi
    def create_order(self):
        order_vals = {
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist.id,
            'scale': self.scale.id,
            'coast_pilot': self.user_id.id,
            'fiscal_position_id': self.fiscal_position.id,
            'type': self.type,
            'operation_start_time': self.operation_start_time,
            'operation_end_time': self.operation_end_time,
        }
        new_order = self.env['sale.order'].create(order_vals)
        if self.type:
            prods = [self.env.ref('port_scale_sale.product_%s' % self.type)]
            if self.type == 'undocking':
                prods.append(self.env.ref('port_scale_sale.product_out'))
            if self.type == 'move':
                prods.append(self.env.ref('port_scale_sale.product_docking'))
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
                line_vals = new_line._convert_to_write(
                    new_line._cache)

                new_line = self.env['sale.order.line'].create(line_vals)
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = "[('id', '=', " + str(new_order.id) + ")]"
        return action
