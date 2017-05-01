# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class OrderLinesReport(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, orders):
        sheet = workbook.add_worksheet('1')
        pos = 1
        header = [u'Escala', u'Tipo', u'Zona', u'Fecha solicitud',
                  u'Fecha inicio', u'Fecha fin', u'Barco', u'Bandera', u'G.T.',
                  u'Remolcadores', u'Práctico', u'Incidencias',
                  u'Reclamaciones', u'Total', u'Muelle']
        sheet.write_row(0, 0, header)
        type_dict = {'docking': 'Atraque',
                     'undocking': 'Desatraque',
                     'move': 'Movimiento',
                     'in': 'Entrada'}
        for order in orders:
            for line in order.order_line:
                start_date = end_date = ''
                if order.operation_start_time:
                    start_date = fields.Datetime.from_string(
                        order.operation_start_time).strftime(
                        '%d/%m/%Y %H:%M:%S')
                if order.operation_end_time:
                    end_date = fields.Datetime.from_string(
                        order.operation_end_time).strftime(
                        '%d/%m/%Y %H:%M:%S')
                order_type = ''
                if order.type:
                    order_type = type_dict[order.type]
                order_row = [
                    order.name, order_type, line.zone, '',
                    start_date, end_date,
                    order.scale.ship.name, order.scale.ship.country.name,
                    order.scale.ship.gt, order.scale.tug_number,
                    order.user_id.name, '', '', order.amount_total,
                    order.scale.dock.name]
                sheet.write_row(pos, 0, order_row)
                pos += 1
        for i in range(len(header)):
            sheet.set_column(i, 0, 20)


OrderLinesReport('report.sale.order.lines.xlsx', 'sale.order')
