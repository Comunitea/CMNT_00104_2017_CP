# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from datetime import datetime
from .tug_data import TUG_SELECTOR


class PortScale(models.Model):

    _name = 'port.scale'

    name = fields.Char('Nº escala')
    ship = fields.Many2one('ship', required=True)
    gt = fields.Integer("GT",related="ship.gt", readonly=True)
    origin = fields.Char()
    operation = fields.Selection(
        (('D', 'disembarkation'),
         ('E', 'embarkation'),
         ('T', 'transfer'),
         ('R', 'scraps')))
    draft = fields.Float()
    eta = fields.Datetime()
    scale_state = fields.Char()  # selection?
    fondeo_previo = fields.Boolean()
    docking_state = fields.Selection(
        (('a', 'a'), ('b', 'b')))  # ???
    docking = fields.Char()
    observaciones = fields.Char()
    dock = fields.Many2one('port.dock')
    state = fields.Selection(
        (('input', 'Input'), ('anchoring', 'Anchoring'),
         ('departure', 'Departure'), ('done', 'Done')), default='input')

    docking_start_time = fields.Datetime()
    docking_end_time = fields.Datetime()
    anchor_start_time = fields.Datetime()
    anchor_end_time = fields.Datetime()
    undocking_start_time = fields.Datetime()
    undocking_end_time = fields.Datetime()
    change_docking_start_time = fields.Datetime()
    change_docking_end_time = fields.Datetime()
    quality_signature = fields.Binary()
    quality_service_satisfaction = fields.Integer()
    norays = fields.Char()
    tug_number = fields.Selection(TUG_SELECTOR)

    def start_docking(self):
        self.docking_start_time = datetime.now()

    def end_docking(self):
        self.docking_end_time = datetime.now()
        self.state = 'departure'

    def start_anchor(self):
        self.anchor_start_time = datetime.now()

    def end_anchor(self):
        self.anchor_end_time = datetime.now()
        self.state = 'anchoring'

    def anchor_without_coast_pilot(self):
        self.state = 'anchoring'

    def start_undocking(self):
        self.undocking_start_time = datetime.now()

    def end_undocking(self):
        self.undocking_end_time = datetime.now()
        self.state = 'done'

    def start_change_docking(self):
        self.change_docking_start_time = datetime.now()

    def end_change_docking(self):
        self.change_docking_end_time = datetime.now()
