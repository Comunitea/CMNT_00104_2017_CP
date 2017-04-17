# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class PortScale(models.Model):

    _inherit = 'port.scale'

    def _create_order(self, type):
        action = self.env.ref(
            'port_scale_sale.port_scale_create_order_action').read()[0]
        context = dict(self._context)
        context['sale_type'] = type
        action['context'] = str(context)
        return action

    def end_docking(self):
        super(PortScale, self).end_docking()
        return self._create_order('docking')

    def end_anchor(self):
        super(PortScale, self).end_anchor()
        return self._create_order('in')

    def end_undocking(self):
        super(PortScale, self).end_undocking()
        return self._create_order('undocking')

    def end_change_docking(self):
        super(PortScale, self).end_change_docking()
        return self._create_order('move')
