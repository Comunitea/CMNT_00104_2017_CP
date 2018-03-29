# -*- coding: utf-8 -*-
# © 2018 Alberto Luengo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from datetime import date, timedelta, datetime
import os


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
        return

    @api.model
    def cron_check_portel_history(self):
        """
        Si detectamos que entre la fecha y hora actual y la última importacion de Portel ha pasado + de 30 minutos
        llamamos al script de reinicio presente en /home/odoo
        """
        last_scale_importation = self.search([],limit=1, order='date_execution DESC')
        port_scale_facade = self.env['port.scale']
        right_now = fields.Datetime.now()
        d1 = datetime.strptime(right_now, "%Y-%m-%d %H:%M:%S")
        d2 = datetime.strptime(last_scale_importation.date_execution, "%Y-%m-%d %H:%M:%S")
        difference = d1 - d2
        diff_as_tuple = divmod(difference.days * 86400 + difference.seconds, 60)
        #Esto nos da una tupla de minutos, segundos
        if diff_as_tuple[0] >= 30:
            #Fuerzo la llamada del metodo que consume el webservice de Portel
            port_scale_facade.import_api_data()
            #os.system('echo odoo2017 | sudo -S sh /home/odoo/reinicio_odoo.sh')
            #os.system('sh /home/odoo/reinicio_odoo.sh')
        return

    date_execution = fields.Datetime(string='Fecha Ejecución', required=True)
    scale_id = fields.Many2one('port.scale', string='Escala',required=True)
    ship_id = fields.Many2one('ship', string='Buque',required=True)
    operations_performed = fields.Text('Operaciones realizadas')