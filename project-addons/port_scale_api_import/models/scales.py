# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from zeep import Client
from lxml import etree
import logging
from odoo import models, api, tools
from datetime import datetime, timedelta
import time

_logger = logging.getLogger(__name__)


class PortScale(models.Model):
    _inherit = 'port.scale'

    ERROR_CODES = {
        '01': 'IP no autorizada',
        '02': 'No hay resultados',
        '03': 'No hay conexión con la BD del DUE',
        '04': 'No se ha configurado la cadena de conexión',
        '90': 'Error conexión BD DUE',
        '91': 'Error subproceso anulado',
        '92': 'Error tiempo de espera caducado',
        '93': 'Error en el nivel de transporte',
        '94': 'Error de bloqueo',
        '95': 'Error en el envío de correo',
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
        scale_history_facade = self.env['port.scale.history']
        try:
            api_url = self.env['ir.config_parameter'].get_param('port.scale.api.url')
            api_method = self.env['ir.config_parameter'].get_param('port.scale.api.method')
            if not api_url or not api_method:
                scale_history_operations = '***[ERROR] NO SE HA ENCONTRADO EL WEBSERVICE O LA URL EN ODOO***'
                scale_history_vals = {
                    'date_execution': datetime.now(),
                    'scale_id': 2,
                    'ship_id': 1,
                    'operations_performed': scale_history_operations
                }
                scale_history_facade.create(scale_history_vals)
                print "**** %s" %(scale_history_vals)
                return True
            #Hacemos la llamada
            #http://docs.python-zeep.org/en/master/client.html#configuring-the-client
            try:
                print "************ ANTES DE INSTANCIAR EL CLIENTE *************"
                scales_client = Client(api_url)
                #To set a transport timeout use the timeout option.The default timeout is 300 seconds
                current_time_before = datetime.now()
                print "************ ANTES DE LLAMAR AL SERVICE *************"
                scales_data = scales_client.service[api_method]()
                print "************ DESPUES DE LLAMAR AL SERVICE *************"
                #scales_data = "<Res_CORUNA_PILOTS><LIS_ESCALAS><STATUS>91</STATUS><DESCRIPCION>Error subproceso anulado</DESCRIPCION><NUM_ESCALA/><CONSIGNATARIO/><IMO/><MMSI/><CALLSIGN/><BANDERA/><BUQUE/><GT/><ESTADO/><ETA/><ETD/><DESPACHADO_SALIDA/><PUERTO_ANTERIOR/><MUELLE/><CALADO_LLEGADA/><NORAYS/><ESTADO_ATRAQUE/><FONDEO_PREVIO/><COSTADO_ATRAQUE/><OPERACION/><CARGA/><CANTIDAD/></LIS_ESCALAS></Res_CORUNA_PILOTS>"
                scales_data_forced = scales_data[scales_data.find("<"):]
                xml_doc = etree.fromstring(scales_data_forced)
                print "************ DESPUES DE OBTENER XML DOC *************"
                current_time_after = datetime.now()
                difference = current_time_after - current_time_before
                seconds_tuple = divmod(difference.days * 86400 + difference.seconds, 60)
                if seconds_tuple[0] > 5:
                    print "************ OBTENGO TIMEOUT Y SALGO*************"
                    return True
            except Exception as e:
                failure_reason = tools.ustr(e)
                scale_history_operations = '***[ERROR] NO SE HAN DEVUELTO VALORES DESDE PORTEL: %s***' % (failure_reason)
                scale_history_vals = {
                    'date_execution': datetime.now(),
                    'scale_id': 2,
                    'ship_id': 1,
                    'operations_performed': scale_history_operations
                }
                scale_history_facade.create(scale_history_vals)
                print "[ERROR] NO SE HAN DEVUELTO VALORES DESDE PORTEL: **** %s" %(scale_history_vals)
                return True
            for scale_element in xml_doc.iter('LIS_ESCALAS'):
                status_code = scale_element.findtext('STATUS')
                if status_code != '**':
                    try:
                        scale_history_operations = '%s->%s: %s' % (status_code, self.ERROR_CODES[status_code], scale_element.findtext('DESCRIPCION'))
                        scale_history_vals = {
                            'date_execution': datetime.now(),
                            'scale_id': 2,
                            'ship_id': 1,
                            'operations_performed': scale_history_operations
                        }
                        scale_history_facade.create(scale_history_vals)
                        print "[ERROR] DEVUELVO CODIGO DE ERROR Y ACABO: **** %s" %(scale_history_vals)
                        return True
                    except:
                        return True
                # [06/08/18] No importamos ninguna escala que no sea del año actual
                # [26/12/18] No importamos ninguna escala con una ETA de más de 3 meses de antigüedad
                scale_name = scale_element.findtext('NUM_ESCALA')
                # current_year = datetime.today().year
                eta = etd = '2099-12-31'
                if scale_element.findtext('ETA'):
                    eta = self.parse_api_datetime(scale_element.findtext('ETA'))
                today_three_months_ago = datetime.today()- timedelta(3*365/12)
                # if scale_name[0:4] =='****' or (scale_name[0:4]!='****' and int(scale_name[0:4]) == current_year):
                #if scale_name[0:4] == '****' or (scale_name[0:4] != '****' and eta>=today_three_months_ago):
                if eta>=today_three_months_ago:
                    ship_vals = {'name': scale_element.findtext('BUQUE')}
                    scale_history_operations = ''
                    if scale_element.findtext('ETD'):
                        etd = self.parse_api_datetime(scale_element.findtext('ETD'))

                    scale_vals = {
                        'name': scale_element.findtext('NUM_ESCALA'),
                        'scale_state': scale_element.findtext('ESTADO'),
                        'origin': scale_element.findtext('PUERTO_ANTERIOR'),
                        'partner_name': scale_element.findtext('CONSIGNATARIO')
                    }
                    partner = self.env['res.partner'].search([('name', '=', scale_element.findtext('CONSIGNATARIO'))])
                    if partner:
                        scale_vals['partner_id'] = partner.id

                    if scale_element.findtext('IMO'):
                        ship_vals['imo'] = scale_element.findtext('IMO')

                    if scale_element.findtext('MMSI'):
                        ship_vals['mmsi'] = scale_element.findtext('MMSI')

                    if scale_element.findtext('BANDERA'):
                        country = self.env['res.country'].search([('code', '=', scale_element.findtext('BANDERA'))])
                        if country:
                            ship_vals['country'] = country.id
                    if scale_element.findtext('CALLSIGN'):
                        ship_vals['callsign'] = scale_element.findtext('CALLSIGN')

                    if scale_element.findtext('CALADO_LLEGADA'):
                        scale_vals['draft'] = scale_element.findtext('CALADO_LLEGADA')
                    if scale_element.findtext('GT'):
                        ship_vals['gt'] = float(scale_element.findtext('GT'))
                    if scale_element.findtext('ESTADO_ATRAQUE'):
                        scale_vals['docked_state'] = scale_element.findtext('ESTADO_ATRAQUE')
                    if scale_element.findtext('FONDEO_PREVIO'):
                        scale_vals['fondeo_previo'] = self.BOOL_API[scale_element.findtext('FONDEO_PREVIO')]
                    if scale_element.findtext('OPERACION'):
                        scale_vals['operation'] = scale_element.findtext('OPERACION')
                    if scale_element.findtext('CARGA'):
                        scale_vals['load'] = scale_element.findtext('CARGA')
                    if scale_element.findtext('CANTIDAD'):
                        scale_vals['load_qty'] = scale_element.findtext('CANTIDAD')
                    if scale_element.findtext('COSTADO_ATRAQUE'):
                        scale_vals['dock_side'] = scale_element.findtext('COSTADO_ATRAQUE')

                    created_ships = False
                    if ship_vals.get('imo', False):
                        created_ships = self.env['ship'].search([('imo', '=', ship_vals['imo'])])
                    if not created_ships and ship_vals.get('mmsi', False):
                        created_ships = self.env['ship'].search([('mmsi', '=', ship_vals['mmsi'])])

                    if not created_ships and ship_vals.get('country', False) and ship_vals.get('callsign', False):
                        created_ships = self.env['ship'].search([('country', '=', ship_vals['country']),('callsign', '=', ship_vals['callsign'])])

                    if created_ships:
                        created_ship = created_ships[0]
                        try:
                            created_ship.write(ship_vals)
                            scale_history_operations += "Buque ACTUALIZADO con valores: %s\n" % (ship_vals)
                        except:
                            scale_history_operations += "NO SE HA PODIDO ACTUALIZAR el buque con valores: %s\n" % (ship_vals)
                    else:
                        created_ship = self.env['ship'].create(ship_vals)
                        scale_history_operations += "Buque CREADO con valores: %s\n" % (ship_vals)

                    scale_vals['ship'] = created_ship.id

                    if scale_element.findtext('MUELLE'):
                        try:
                            created_docks = self.env['port.dock'].search([('name', '=', scale_element.findtext('MUELLE'))])
                            if not created_docks:
                                created_dock = self.env['port.dock'].create({'name': scale_element.findtext('MUELLE')})
                            else:
                                created_dock = created_docks[0]
                            scale_vals['dock'] = created_dock.id
                        except:
                            scale_history_operations += "[ERROR] NO SE HA PODIDO ACTUALIZAR la escala con valores: %s\n" % (scale_element)

                    if scale_element.findtext('NORAYS'):
                        scale_vals['norays'] = scale_element.findtext('NORAYS')
                    if scale_element.findtext('DESPACHADO_SALIDA'):
                        scale_vals['departure_authorization'] = self.BOOL_API[scale_element.findtext('DESPACHADO_SALIDA')]

                    created_scales = []
                    if scale_vals.get('ship') and scale_vals.get('name'):
                        try:
                            created_scales = self.env['port.scale'].search([('ship', '=', scale_vals['ship']),('name', '=', scale_vals['name']),'|',('active', '=', True), ('active', '=', False)])
                        except:
                            created_scales = []
                    else:
                        created_scales = []

                    # [05/12/17] Si los campos ETA, ETD, Calado (draft), Muelle (dock), Norais (norays), Costado de atraque (dock_side), GT
                    # se modifican por el usuario no se pueden machacar con los que nos vienen de Portel
                    # [13/01/18] No puedo controlar que el cambio lo haga Portel u otro usuario, por lo que solo controlo que sean distintos
                    if created_scales:
                        for created_scale in created_scales:
                            #print "*** ME METO EN created_scales"
                            #print "*** SCALE_VALS_KEYS: %s" %(scale_vals.keys())
                            #print "*** SCALE_VALS: %s" %(scale_vals)
                            #print "*** CREATED_SCALE.do_not_update_eta: %s"%(created_scale.do_not_update_eta)
                            #print "*** CREATED_SCALE.do_not_update_etd: %s"%(created_scale.do_not_update_etd)
                            #print "*** CREATED_SCALE.do_not_update_draft: %s"%(created_scale.do_not_update_draft)
                            #print "*** CREATED_SCALE.do_not_update_dock: %s"%(created_scale.do_not_update_dock)
                            #print "*** CREATED_SCALE.do_not_update_norays: %s"%(created_scale.do_not_update_norays)
                            #print "*** CREATED_SCALE.do_not_update_dock_side: %s"%(created_scale.do_not_update_dock_side)
                            #print "*** CREATED_SCALE.do_not_update_gt: %s"%(created_scale.do_not_update_gt)
                            if 'eta' in scale_vals.keys() and created_scale.do_not_update_eta:
                                del scale_vals['eta']
                            if 'etd' in scale_vals.keys() and created_scale.dot_not_update_etd:
                                del scale_vals['etd']
                            if 'draft' in scale_vals.keys() and created_scale.do_not_update_draft:
                                del scale_vals['draft']
                            if 'dock' in scale_vals.keys() and created_scale.do_not_update_dock:
                                del scale_vals['dock']
                            if 'norays' in scale_vals.keys() and created_scale.do_not_update_norays:
                                del scale_vals['norays']
                            if 'dock_side' in scale_vals.keys() and created_scale.do_not_update_dock_side:
                                del scale_vals['dock_side']
                            if 'gt' in scale_vals.keys() and created_scale.do_not_update_gt:
                                del scale_vals['gt']
                            #print "*** ACABO DE COMPROBAR EN created_scales"
                            created_scale.write(scale_vals)
                            #print "*** ESCRIBO EN LA ESCALA EN created_scales"
                            scale_history_operations += "Escala creada ACTUALIZADA con valores: %s\n" % (scale_vals)
                            scale_history_vals = {
                                'date_execution': datetime.now(),
                                'scale_id': created_scale.id,
                                'ship_id': created_scale.ship and created_scale.ship.id or False,
                                'operations_performed': scale_history_operations
                            }
                            scale_history_facade.create(scale_history_vals)
                            #print "*** CREO EL HISTORICO EN created_scales"
                    else:
                        # Buscamos si hay alguna escala como enviada para este barco
                        sendend_scales = self.env['port.scale'].search([('ship', '=', scale_vals['ship']),('name', '=', '****'),'|', ('active', '=', True), ('active', '=', False)])
                        if sendend_scales:
                            for sendend_scale in sendend_scales:
                                if 'eta' in scale_vals.keys() and sendend_scale.do_not_update_eta:
                                    del scale_vals['eta']
                                if 'etd' in scale_vals.keys() and sendend_scale.dot_not_update_etd:
                                    del scale_vals['etd']
                                if 'draft' in scale_vals.keys() and sendend_scale.do_not_update_draft:
                                    del scale_vals['draft']
                                if 'dock' in scale_vals.keys() and sendend_scale.do_not_update_dock:
                                    del scale_vals['dock']
                                if 'norays' in scale_vals.keys() and sendend_scale.do_not_update_norays:
                                    del scale_vals['norays']
                                if 'dock_side' in scale_vals.keys() and sendend_scale.do_not_update_dock_side:
                                    del scale_vals['dock_side']
                                if 'gt' in scale_vals.keys() and sendend_scale.do_not_update_gt:
                                    del scale_vals['gt']

                                sendend_scale.write(scale_vals)
                                scale_history_operations += "Escala enviada ACTUALIZADA con valores: %s\n" % (scale_vals)
                                scale_history_vals = {
                                    'date_execution': datetime.now(),
                                    'scale_id': sendend_scale.id,
                                    'ship_id': sendend_scale.ship and sendend_scale.ship.id or False,
                                    'operations_performed': scale_history_operations
                                }
                                #print "**** %s" %(scale_history_vals)
                                scale_history_facade.create(scale_history_vals)
                        else:
                            scale_vals['eta'] = eta
                            scale_vals['etd'] = etd
                            created_scale = self.env['port.scale'].create(scale_vals)
                            scale_history_operations += "Escala CREADA con valores: %s\n" % (scale_vals)
                            scale_history_vals = {
                                'date_execution': datetime.now(),
                                'scale_id': created_scale.id,
                                'ship_id': created_scale.ship and created_scale.ship.id or False,
                                'operations_performed': scale_history_operations
                            }
                            #print "**** %s" %(scale_history_vals)
                            scale_history_facade.create(scale_history_vals)
        except Exception as e:
            failure_reason = tools.ustr(e)
            scale_history_operations = '***[ERROR] SE HA PRODUCIDO UN ERROR EN LA IMPORTACION: %s***'%(failure_reason)
            scale_history_vals = {
                'date_execution': datetime.now(),
                'scale_id': 2,
                'ship_id': 1,
                'operations_performed': scale_history_operations
            }
            #print "**** %s" %(scale_history_vals)
            scale_history_facade.create(scale_history_vals)
            #print "**** ACABO EL CRON POR EL EXCEPT"
            return True
        finally:
            #print "*** ACABO EL CRON POR EL FINALLY"
            return True
