# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Port scale sales',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'port_scale',
        'sale'
    ],
    'data': [
        'data/product.xml',
        'views/account_invoice.xml',
        'views/sale.xml',
        'wizard/port_scale_create_order.xml'
    ],
}