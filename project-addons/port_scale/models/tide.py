# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from datetime import date


class PortTide(models.Model):

    _name = 'port.tide'

    date = fields.Date()
    bajamar_1 = fields.Char()
    bajamar_2 = fields.Char()
    pleamar_1 = fields.Char()
    pleamar_2 = fields.Char()

    @api.model
    def get_today_tides(self):
        tide = self.search([('date', '=', date.today())])
        if not tide:
            return [('Bajamar', '-', '-'), ('Pleamar', '-', '-')]
        return [('Bajamar', tide[0].bajamar_1, tide[0].bajamar_2), ('Pleamar', tide[0].pleamar_1, tide[0].pleamar_2)]
