# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, tools
from datetime import datetime
from pytz import timezone


class PortTug(models.Model):
    _name = 'port.tug'

    name = fields.Char()


class PortScale(models.Model):

    _name = 'port.scale'
    _order = 'eta desc'

    name = fields.Char('Nº escala')
    active = fields.Boolean(default=True)
    ship = fields.Many2one('ship', required=True)
    ship_num_cr = fields.Integer(string="CR", related="ship.attachment_count")
    gt = fields.Float("GT", related="ship.gt")
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
    docked_state = fields.Char()
    fondeo_previo = fields.Boolean()
    observaciones = fields.Char()
    dock = fields.Many2one('port.dock')
    state = fields.Selection(
        (('input', 'Input'), ('anchoring', 'Anchoring'),
         ('departure', 'Departure'), ('done', 'Done')), default='input')
    docking_start_time = fields.Datetime(copy=False)
    docking_end_time = fields.Datetime(copy=False)
    anchor_start_time = fields.Datetime(copy=False)
    anchor_end_time = fields.Datetime(copy=False)
    undocking_start_time = fields.Datetime(copy=False)
    undocking_end_time = fields.Datetime(copy=False)
    change_docking_start_time = fields.Datetime(copy=False)
    change_docking_end_time = fields.Datetime(copy=False)
    quality_signature = fields.Binary()
    quality_service_satisfaction = fields.Integer()
    quality_sign_date = fields.Date()
    norays = fields.Char()
    tugs_in = fields.Many2many('port.tug', 'scale_tugs_in_relation')
    tugs_out = fields.Many2many('port.tug', 'scale_tugs_out_relation')
    tugs_move = fields.Many2many('port.tug', 'scale_tugs_move_relation')
    load = fields.Char()
    load_qty = fields.Float()
    departure_authorization = fields.Boolean()
    dock_side = fields.Char()
    partner_name = fields.Char('Consignatario')
    partner_id = fields.Many2one('res.partner', 'Consignatario')
    input_request_date = fields.Datetime()
    anchoring_request_date = fields.Datetime()
    departure_request_date = fields.Datetime()
    request_date = fields.Datetime(string="Fecha Solicitud Operación")
    has_been_modified = fields.Boolean('Modificada?')
    modified_info = fields.Text('Modificaciones')
    do_not_update_eta = fields.Boolean('Obviar ETA Portel?')
    do_not_update_etd = fields.Boolean('Obviar ETD Portel?')
    do_not_update_draft = fields.Boolean('Obviar Calado Portel?')
    do_not_update_dock = fields.Boolean('Obviar Muelle Portel?')
    do_not_update_norays = fields.Boolean('Obviar Norays Portel?')
    do_not_update_dock_side = fields.Boolean('Obviar Costado de Atraque Portel?')
    do_not_update_gt = fields.Boolean('Obviar GT Portel?')

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
        #self.docking_end_time = datetime.now()
        self.state = 'departure'

    def start_anchor(self):
        self.anchor_start_time = datetime.now()

    def end_anchor(self):
        #self.anchor_end_time = datetime.now()
        self.state = 'anchoring'

    def anchor_without_coast_pilot(self):
        self.state = 'anchoring'

    def docking_without_coast_pilot(self):
        self.state = 'departure'

    def start_undocking(self):
        self.undocking_start_time = datetime.now()

    def end_undocking(self):
        #self.undocking_end_time = datetime.now()
        self.state = 'done'

    def start_change_docking(self):
        self.change_docking_start_time = datetime.now()

    def end_change_docking(self):
        return True
        #self.change_docking_end_time = datetime.now()

    @api.multi
    def unlink(self):
        return self.write({'active': False})

    @api.multi
    def write(self, values):
        """
        # [05/12/17] Si los campos ETA, ETD, Calado (draft), Muelle (dock), Norais (norays), Costado de atraque (dock_side), GT
        # se modifican por el usuario no se pueden machacar con los que nos vienen de Portel
        # [13/01/18] Si el cambio lo realiza un usuario distinto de 1 (Administrador, el que lanza el cron), registro los cambios
        :param values:
        :return:
        """
        if self.env.user.id != 1:
            scale_fields = ['eta','etd','draft','dock','norays','dock_side']
            if 'eta' in values.keys():
                values.update({'do_not_update_eta': True})
            if 'etd' in values.keys():
                values.update({'do_not_update_etd': True})
            if 'draft' in values.keys():
                values.update({'do_not_update_draft': True})
            if 'dock' in values.keys():
                values.update({'do_not_update_dock': True})
            if 'norays' in values.keys():
                values.update({'do_not_update_norays': True})
            if 'dock_side' in values.keys():
                values.update({'do_not_update_dock_side': True})
            if 'gt' in values.keys():
                values.update({'do_not_update_gt': True})

            fmt ="%d-%m-%Y %H:%M:%S"
            # Convert to Europe/Berlin time zone
            now_berlin = datetime.now(timezone('UTC')).astimezone(timezone('Europe/Berlin'))

            modified_text = 'La ultima vez que se ha modificado la escala ha sido el %s por %s y se han cambiado los campos: %s'%(now_berlin.strftime(fmt), self.env.user.name, values)
            values.update({'has_been_modified':True,'modified_info': modified_text})

        return super(PortScale, self).write(values)
