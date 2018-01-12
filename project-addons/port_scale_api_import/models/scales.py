# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from zeep import Client
from lxml import etree
import logging
from odoo import models, api
from datetime import datetime, timedelta

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

    def parse_api_datetime(self, datetime_str):
        # Pasamos a gmt
        ret = datetime.strptime(datetime_str[0:19], '%Y-%m-%dT%H:%M:%S')
        if datetime_str[19] == '+':
            ret -= timedelta(
                hours=int(datetime_str[20:22]), minutes=int(datetime_str[23:]))
        elif datetime_str[18] == '-':
            ret += timedelta(
                hours=int(datetime_str[19:22]), minutes=int(datetime_str[23:]))
        return ret

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
            eta = etd = ''
            if scale_element.findtext('ETA'):
                eta = self.parse_api_datetime(scale_element.findtext('ETA'))
            if scale_element.findtext('ETD'):
                etd = self.parse_api_datetime(scale_element.findtext('ETD'))

            #[05/12/17] Si los campos ETA, ETD, Calado (draft), Muelle (dock), Norais (norays), Costado de atraque (dock side)
            # se modifican por el usuario no se pueden machacar con los que nos vienen de Portel

            scale_vals = {
                'name': scale_element.findtext('NUM_ESCALA'),
                'scale_state': scale_element.findtext('ESTADO'),
                'origin': scale_element.findtext('PUERTO_ANTERIOR'),
                'partner_name': scale_element.findtext('CONSIGNATARIO')
            }
            partner = self.env['res.partner'].search(
                [('name', '=', scale_element.findtext('CONSIGNATARIO'))])
            if partner:
                scale_vals['partner_id'] = partner.id

            if scale_element.findtext('IMO'):
                ship_vals['imo'] = scale_element.findtext('IMO')

            if scale_element.findtext('MMSI'):
                ship_vals['mmsi'] = scale_element.findtext('MMSI')

            if scale_element.findtext('BANDERA'):
                country = self.env['res.country'].search(
                    [('code', '=', scale_element.findtext('BANDERA'))])
                if country:
                    ship_vals['country'] = country.id
            if scale_element.findtext('CALLSIGN'):
                ship_vals['callsign'] = scale_element.findtext('CALLSIGN')

            if scale_element.findtext('CALADO_LLEGADA'):
                scale_vals['draft'] = scale_element.findtext(
                    'CALADO_LLEGADA')
            if scale_element.findtext('GT'):
                ship_vals['gt'] = float(scale_element.findtext(
                    'GT'))
            if scale_element.findtext('ESTADO_ATRAQUE'):
                scale_vals['scale_state'] = scale_element.findtext(
                    'ESTADO_ATRAQUE')
            if scale_element.findtext('FONDEO_PREVIO'):
                scale_vals['fondeo_previo'] = self.BOOL_API[
                    scale_element.findtext('FONDEO_PREVIO')]
            if scale_element.findtext('OPERACION'):
                scale_vals['operation'] = scale_element.findtext('OPERACION')
            if scale_element.findtext('CARGA'):
                scale_vals['load'] = scale_element.findtext('CARGA')
            if scale_element.findtext('CANTIDAD'):
                scale_vals['load_qty'] = scale_element.findtext('CANTIDAD')
            if scale_element.findtext('COSTADO_ATRAQUE'):
                scale_vals['dock_side'] = scale_element.findtext('COSTADO_ATRAQUE')

            created_ship = False
            if ship_vals.get('imo', False):
                created_ship = self.env['ship'].search(
                    [('imo', '=', ship_vals['imo'])])
            if not created_ship and ship_vals.get('mmsi', False):
                created_ship = self.env['ship'].search(
                    [('mmsi', '=', ship_vals['mmsi'])])

            if not created_ship and ship_vals.get('country', False) and \
                    ship_vals.get('callsign', False):
                created_ship = self.env['ship'].search(
                    [('country', '=', ship_vals['country']),
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
            if scale_element.findtext('DESPACHADO_SALIDA'):
                scale_vals['departure_authorization'] = self.BOOL_API[
                    scale_element.findtext('DESPACHADO_SALIDA')]
            created_scales = self.env['port.scale'].search(
                [('ship', '=', scale_vals['ship']),
                 ('name', '=', scale_vals['name']),
                 '|', ('active', '=', True), ('active', '=', False)])

            # [05/12/17] Si los campos ETA, ETD, Calado (draft), Muelle (dock), Norais (norays), Costado de atraque (dock_side)
            # se modifican por el usuario no se pueden machacar con los que nos vienen de Portel
            #[13/01/18] No puedo controlar que el cambio lo haga Portel u otro usuario, por lo que solo controlo que sean distintos
            if created_scales:
                for created_scale in created_scales:
                    if not created_scale.eta:
                        scale_vals['eta'] = eta
                    if not created_scale.etd:
                        scale_vals['etd'] = etd

                    if 'draft' in scale_vals and created_scale.draft and created_scale.draft != scale_vals['draft']:
                        del scale_vals['draft']
                    if 'dock' in scale_vals and created_scale.dock and created_scale.dock.id != scale_vals['dock']:
                        del scale_vals['dock']
                    if 'norays' in scale_vals and created_scale.norays and created_scale.norays != scale_vals['norays']:
                        del scale_vals['norays']
                    if 'dock_side' in scale_vals and created_scale.dock_side and created_scale.dock_side != scale_vals['dock_side']:
                        del scale_vals['dock_side']

                    created_scale.write(scale_vals)
            else:
                #Buscamos si hay alguna escala como enviada para este barco
                sendend_scales = self.env['port.scale'].search(
                    [('ship', '=', scale_vals['ship']),
                     ('name', '=', '****'),
                     '|', ('active', '=', True), ('active', '=', False)])
                if sendend_scales:
                    for sendend_scale in sendend_scales:
                        if not sendend_scale.eta:
                            scale_vals['eta'] = eta
                        if not sendend_scale.etd:
                            scale_vals['etd'] = etd

                        if 'draft' in scale_vals and sendend_scale.draft and sendend_scale.draft != scale_vals['draft']:
                            del scale_vals['draft']
                        if 'dock' in scale_vals and sendend_scale.dock and sendend_scale.dock.id != scale_vals['dock']:
                            del scale_vals['dock']
                        if 'norays' in scale_vals and sendend_scale.norays and sendend_scale.norays != scale_vals['norays']:
                            del scale_vals['norays']
                        if 'dock_side' in scale_vals and sendend_scale.dock_side and sendend_scale.dock_side != scale_vals['dock_side']:
                            del scale_vals['dock_side']

                        sendend_scale.write(scale_vals)
                else:
                    scale_vals['eta'] = eta
                    scale_vals['etd'] = etd
                    self.env['port.scale'].create(scale_vals)
