# © 2019 TKOpen <https://tkopen.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'First Login Change Password',
    'summary': 'Force users to change password on first login',
    'author': 'TKOpen',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'website': 'https://tkopen.com',
    'version': '12.0.0.0.0',
    'sequence': 10,
    'depends': [
        'auth_signup',
        'web',
    ],
    'data': [],
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'test': [],
    'images': ['static/description/icon.png'],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}
