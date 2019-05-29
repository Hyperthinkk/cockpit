# -*- encoding: utf-8 -*-

{
    'name': 'SMTP Server Per User',
    'category': 'Mail',
    'author': 'TKOPEN',
    'license': 'AGPL-3',
    'website': 'https://tkopen.com',
    'version': '12.0.2',
    'sequence': 10,
    'depends': [
        'base',
        'mail',
        'web_notify'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mail_server_config_view.xml',
        'views/templates.xml'
    ],
    "price": 9,
    "currency": 'EUR',
    'init': [],
    'demo': [],
    'update': [],
    "images": ['static/description/thumbnail.png'],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False,
    'certificate': '',
    'qweb': ['static/src/xml/systray.xml',]
}
