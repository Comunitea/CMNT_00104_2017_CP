# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class PortScale(models.Model):

    _name = 'port.scale'

    name = fields.Char('Nº escala')
    ship = fields.Many2one('ship', required=True)
    gt = fields.Integer()
    origin = fields.Char()
    operation = fields.Selection(
        (('D', 'disembarkation'),
         ('E', 'embarkation'),
         ('T', 'transfer'),
         ('R', 'scraps')))
    calado_llegada = fields.Float()
    eta = fields.Datetime()
    scale_state = fields.Char()  # selection?
    fondeo_previo = fields.Boolean()
    estado_atraque = fields.Selection(
        (('a', 'a'), ('b', 'b')))  # ???
    atraque = fields.Char()
    observaciones = fields.Char()
    dock = fields.Many2one('port.dock')
