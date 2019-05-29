# -*- coding: utf-8 -*-
{

    "name": "Odoo Migration Experts Client",
    "description": "Migrate any odoo version to any version with the token from OdooMigrationExperts",
    "category": "Server-Tools",
    "version": "12.0.2",
    "author": "TKOPEN",
    "license": "Other proprietary",
    "website": "https://tkopen.com",
    "depends": [
        'base_setup',
        'mail',
    ],
    "data": [
        'views/res_config.xml',

    ],
    "images": [ 'static/description/banner.png'],
    "application": True,
    "installable": True,
    "auto_install": False,

}
