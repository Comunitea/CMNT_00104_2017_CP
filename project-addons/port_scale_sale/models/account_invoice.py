# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    scale = fields.Many2one('port.scale')
    ship = fields.Many2one('ship', related='scale.ship', store=True)
