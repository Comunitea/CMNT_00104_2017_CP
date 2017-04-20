# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from odoo.addons.port_scale.models.tug_data import TUG_SELECTOR


class PortScaleCreateOrder(models.TransientModel):

    _name = 'port.scale.create.order'

    scale = fields.Many2one('port.scale')
    ship = fields.Many2one('ship', related='scale.ship', required=True)
    docking_start_time = fields.Datetime(related='scale.docking_start_time')
    docking_end_time = fields.Datetime(related='scale.docking_end_time')
    docking = fields.Char(related='scale.docking', required=True)
    flag = fields.Char(related='scale.ship.flag', required=True)
    gt = fields.Integer(related='scale.gt', required=True)
    partner_id = fields.Many2one('res.partner',
                                 related='scale.ship.partner_id',
                                 required=True)
    tug_number = fields.Selection(TUG_SELECTOR, related='scale.tug_number', required=True)
    user_id = fields.Many2one('res.users', 'Coast pilot', required=True)
    pricelist = fields.Many2one('product.pricelist', required=True)
    fiscal_position = fields.Many2one('account.fiscal.position')
    zone = fields.Selection([('A', 'A'), ('B', 'B')], 'Zone', default = 'A',
                            required=True)
    type = fields.Selection(
        (('docking', 'Docking'),
         ('undocking', 'Undocking'),
         ('move', 'Move'),
         ('in', 'In')))

    @api.model
    def default_get(self, fields):
        res = super(PortScaleCreateOrder, self).default_get(fields)
        res['scale'] = self.env['port.scale'].browse(
            self._context.get('active_id', False)).id
        res['type'] = self._context.get('sale_type', False)
        return res

    @api.multi
    def create_order(self):
        order_vals = {
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist.id,
            'scale': self.scale.id,
            'user_id': self.user_id.id,
            'fiscal_position_id': self.fiscal_position.id,
            'type': self.type,
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
                    'price_unit': 0.0,
                    'order_id': new_order.id,
                    'product_uom': False,
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
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = "[('id', '=', " + str(new_order.id) + ")]"
        return action
