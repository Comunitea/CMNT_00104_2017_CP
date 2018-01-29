# -*- coding: utf-8 -*-
# © 2018 Alberto Luengo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from datetime import date, timedelta


class PortScaleHistory(models.Model):
    """
    Almacenamos el historico de operaciones sobre las escalas que realiza el cron
    """
    _name = 'port.scale.history'
    _order = 'date_execution desc'

    @api.model
    def cron_delete_yesterday_info(self):
        """
        Borramos el historico de las importaciones del día anterior
        """
        yesterday = date.today() - timedelta(1)
        first_hour_yesterday = yesterday.strftime('%Y-%m-%d 00:00:01')
        last_hour_yesterday = yesterday.strftime('%Y-%m-%d 23:59:59')
        yesterday_scales_history = self.search([('date_execution','>=',first_hour_yesterday),('date_execution','<=',last_hour_yesterday)])
        if yesterday_scales_history:
            yesterday_scales_history.unlink()


    date_execution = fields.Datetime(string='Fecha Ejecución', required=True)
    scale_id = fields.Many2one('port.scale', string='Escala',required=True)
    ship_id = fields.Many2one('ship', string='Buque',required=True)
    operations_performed = fields.Text('Operaciones realizadas')