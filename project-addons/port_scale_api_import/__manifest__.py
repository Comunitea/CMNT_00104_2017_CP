# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Port scale api import',
    'summary': 'Import scales data from soap api',
    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'port_scale'
    ],
    'data': [
        'data/ir_cron.xml'
    ],
    'external_dependencies': {
        'python': ['zeep'],
        'bin': [],
    },
}
