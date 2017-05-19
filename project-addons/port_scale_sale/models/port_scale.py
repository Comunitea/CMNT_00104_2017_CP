# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class PortScale(models.Model):

    _inherit = 'port.scale'

    def _create_order(self, type, start, end):
        action = self.env.ref(
            'port_scale_sale.port_scale_create_order_action').read()[0]
        context = dict(self._context)
        context['sale_type'] = type
        context['start_time'] = start
        context['end_time'] = end
        action['context'] = str(context)
        return action
