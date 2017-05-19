# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Port scale',
    'summary': 'Manage port scales',
    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'web',
        'web_digital_sign'
    ],
    'data': [
        'wizard/scale_quality.xml',
        'views/scale.xml',
        'views/ship.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/tide.xml',
        'data/ir_cron.xml'
    ],

    'qweb': [
        "static/src/xml/tide_menu.xml",
    ],
}
