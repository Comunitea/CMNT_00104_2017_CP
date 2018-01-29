# -*- coding: utf-8 -*-
# © 2018 Alberto Luengo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class PortScaleHistory(models.Model):
    """
    Almacenamos el historico de operaciones sobre las escalas que realiza el cron
    """
    _name = 'port.scale.history'
    _order = 'date_execution desc'

    date_execution = fields.Datetime(string='Fecha Ejecución', required=True)
    scale_id = fields.Many2one('port.scale', string='Escala',required=True)
    operations_performed = fields.Text('Operaciones realizadas')