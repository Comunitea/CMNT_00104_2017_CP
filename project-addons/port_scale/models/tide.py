# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from datetime import date
from lee_feeds_rss import main


class PortTide(models.Model):

    _name = 'port.tide'

    date = fields.Date()
    bajamar_1 = fields.Char()
    altura_bajamar_1 = fields.Char()
    bajamar_2 = fields.Char()
    altura_bajamar_2 = fields.Char()
    pleamar_1 = fields.Char()
    altura_pleamar_1 = fields.Char()
    pleamar_2 = fields.Char()
    altura_pleamar_2 = fields.Char()

    @api.model
    def get_today_tides(self):
        tide = self.search([('date', '=', date.today())])
        if not tide:
            return [('Bajamar', '-(-)', '-(-)'), ('Pleamar', '-(-)', '-(-)')]
        return [('Bajamar', '%s (%s)' %
                 (tide[0].bajamar_1 or '', tide[0].altura_bajamar_1 or ''),
                 '%s (%s)' % (tide[0].bajamar_2 or '',
                              tide[0].altura_bajamar_2 or '')),
                ('Pleamar', '%s (%s)' %
                 (tide[0].pleamar_1 or '', tide[0].altura_pleamar_1 or ''),
                 '%s (%s)' % (tide[0].pleamar_2 or '',
                              tide[0].altura_pleamar_2 or ''))]

    @api.model
    def import_feed_rss_tides(self):
        tide_dict = main()
        # Sacamos id=1. TODO: cambiar por config?
        tide_list = tide_dict['1+' + date.today().strftime('%d/%m/%Y')]
        vals = {
            'date': date.today(),
            'bajamar_1': tide_list['Bajamar'][0][0],
            'altura_bajamar_1': tide_list['Bajamar'][0][1],
            'pleamar_1': tide_list['Pleamar'][0][0],
            'altura_pleamar_1': tide_list['Pleamar'][0][1],
        }
        if len(tide_list['Bajamar']) > 1:
            vals['bajamar_2'] = tide_list['Bajamar'][1][0]
            vals['altura_bajamar_2'] = tide_list['Bajamar'][1][1]
        else:
            vals['bajamar_2'] = '-'
            vals['altura_bajamar_2'] = '-'
        if len(tide_list['Pleamar']) > 1:
            vals['pleamar_2'] = tide_list['Pleamar'][1][0]
            vals['altura_pleamar_2'] = tide_list['Pleamar'][1][1]
        else:
            vals['pleamar_2'] = '-'
            vals['altura_pleamar_2'] = '-'

        exist_tide = self.env['port.tide'].search(
            [('date', '=', date.today())])
        if exist_tide:
            exist_tide.write(vals)
        else:
            self.env['port.tide'].create(vals)
