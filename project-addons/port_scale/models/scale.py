# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from datetime import datetime


class PortTug(models.Model):
    _name = 'port.tug'

    name = fields.Char()


class PortScale(models.Model):

    _name = 'port.scale'
    _order = 'eta desc'

    name = fields.Char('Nº escala')
    active = fields.Boolean(default=True)
    ship = fields.Many2one('ship', required=True)
    gt = fields.Integer("GT", related="ship.gt", readonly=True)
    origin = fields.Char()
    operation = fields.Selection(
        (('D', 'disembarkation'),
         ('E', 'embarkation'),
         ('T', 'transfer'),
         ('R', 'scraps')))
    draft = fields.Float()
    eta = fields.Datetime()
    etd = fields.Datetime()
    scale_state = fields.Char()  # selection?
    fondeo_previo = fields.Boolean()
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
    quality_sign_date = fields.Date()
    norays = fields.Char()
    tugs_in = fields.Many2many('port.tug')
    tugs_out = fields.Many2many('port.tug')
    reten = fields.Boolean()
    load = fields.Char()
    load_qty = fields.Float()
    departure_authorization = fields.Boolean()
    dock_side = fields.Char()
    partner_name = fields.Char('Consignatario')
    partner_id = fields.Many2one('res.partner', 'Consignatario')
    input_request_date = fields.Datetime()
    anchoring_request_date = fields.Datetime()
    departure_request_date = fields.Datetime()

    @api.multi
    def set_input_request_date(self):
        self.input_request_date = datetime.now()

    @api.multi
    def set_anchoring_request_date(self):
        self.anchoring_request_date = datetime.now()

    @api.multi
    def set_departure_request_date(self):
        self.departure_request_date = datetime.now()

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

    @api.multi
    def unlink(self):
        return self.write({'active': False})
