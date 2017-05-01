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

    def end_docking(self):
        super(PortScale, self).end_docking()
        return self._create_order('docking',
                                  self.docking_start_time,
                                  self.docking_end_time)

    def end_anchor(self):
        super(PortScale, self).end_anchor()
        return self._create_order('in',
                                  self.anchor_start_time,
                                  self.anchor_end_time)

    def end_undocking(self):
        super(PortScale, self).end_undocking()
        return self._create_order('undocking',
                                  self.undocking_start_time,
                                  self.undocking_end_time)

    def end_change_docking(self):
        super(PortScale, self).end_change_docking()
        return self._create_order('move',
                                  self.change_docking_start_time,
                                  self.change_docking_end_time)
