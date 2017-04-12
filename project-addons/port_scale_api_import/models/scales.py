# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from zeep import Client
from lxml import etree
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class PortScale(models.Model):

    _inherit = 'port.scale'

    ERROR_CODES = {
        '01': 'IP no autorizada',
        '02': 'No hay resultados',
        '03': 'No hay conexión con la BD del DUE',
        '04': 'No se ha configurado la cadena de conexión',
        '99': 'Error general',
    }  # ** = correcto

    BOOL_API = {
        'N': False,
        'S': True
    }

    @api.model
    def import_api_data(self):
        api_url = self.env['ir.config_parameter'].get_param(
            'port.scale.api.url')
        api_method = self.env['ir.config_parameter'].get_param(
            'port.scale.api.method')
        if not api_url or not api_method:
            return
        scales_client = Client(api_url)
        scales_data = scales_client.service[api_method]()
        xml_doc = etree.fromstring(scales_data)
        for scale_element in xml_doc.iter('LIS_ESCALAS'):
            status_code = scale_element.findtext('STATUS')
            if status_code != '**':
                _logger.error('%s : %s' %
                              (self.ERROR_CODES[status_code],
                               scale_element.findtext('DESCRIPCION')))
                continue
            ship_vals = {
                'name': scale_element.findtext('BUQUE'),
            }
            scale_vals = {
                'name': scale_element.findtext('NUM_ESCALA'),
                'scale_state': scale_element.findtext('ESTADO'),
                'eta': scale_element.findtext('ETA'),
                'origin': scale_element.findtext('PUERTO_ANTERIOR'),
            }

            partner = self.env['res.partner'].search(
                [('name', '=', scale_element.findtext('CONSIGNATARIO'))])
            if partner:
                ship_vals['partner_id'] = partner.id

            if scale_element.findtext('IMO'):
                ship_vals['imo'] = scale_element.findtext('IMO')

            if scale_element.findtext('MMSI'):
                ship_vals['mmsi'] = scale_element.findtext('MMSI')

            if scale_element.findtext('BANDERA'):
                ship_vals['flag'] = scale_element.findtext('BANDERA')
            if scale_element.findtext('CALLSIGN'):
                ship_vals['callsign'] = scale_element.findtext('CALLSIGN')

            if scale_element.findtext('CALADO_LLEGADA'):
                scale_vals['draft'] = scale_element.findtext(
                    'CALADO_LLEGADA')
            if scale_element.findtext('ESTADO_ATRAQUE'):
                scale_vals['scale_state'] = scale_element.findtext(
                    'ESTADO_ATRAQUE')
            if scale_element.findtext('FONDEO_PREVIO'):
                scale_vals['fondeo_previo'] = self.BOOL_API[
                    scale_element.findtext('FONDEO_PREVIO')]
            if scale_element.findtext('OPERACION'):
                scale_vals['operation'] = scale_element.findtext('OPERACION')

            created_ship = False
            if ship_vals.get('imo', False):
                created_ship = self.env['ship'].search(
                    [('imo', '=', ship_vals['imo'])])
            if not created_ship and ship_vals.get('mmsi', False):
                created_ship = self.env['ship'].search(
                    [('mmsi', '=', ship_vals['mmsi'])])

            if not created_ship and ship_vals.get('flag', False) and \
                    ship_vals.get('callsign', False):
                created_ship = self.env['ship'].search(
                    [('flag', '=', ship_vals['flag']),
                     ('callsign', '=', ship_vals['callsign'])])

            if created_ship:
                created_ship.write(ship_vals)
            else:
                created_ship = self.env['ship'].create(ship_vals)
            scale_vals['ship'] = created_ship.id

            if scale_element.findtext('MUELLE'):
                created_dock = self.env['port.dock'].search(
                    [('name', '=', scale_element.findtext('MUELLE'))])
                if not created_dock:
                    created_dock = self.env['port.dock'].create(
                        {'name': scale_element.findtext('MUELLE')})
                scale_vals['dock'] = created_dock.id
            if scale_element.findtext('NORAYS'):
                scale_vals['norays'] = scale_element.findtext('NORAYS')

            created_scale = self.env['port.scale'].search(
                [('name', '=', scale_vals['name'])])
            if created_scale:
                created_scale.write(scale_vals)
            else:
                self.env['port.scale'].create(scale_vals)
