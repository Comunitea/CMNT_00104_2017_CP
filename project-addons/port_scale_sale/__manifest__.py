# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Port scale sales',
    'summary': '',
    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'port_scale',
        'sale',
        'l10n_es'
    ],
    'data': [
        'data/product.xml',
        'views/sale.xml',
        'wizard/port_scale_create_order.xml',
        'wizard/sale_make_invoice_view.xml'
    ],
}
