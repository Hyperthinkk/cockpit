# -*- coding: utf-8 -*-
{

    "name": "Open Save As Dialog on PDF Report",
    "summary": "This module offers to save PDF report right after opening in browser"
               "Note: This module wouldn't open file right after printing report from odoo. "
               "It creaets a PDF with such properties that whenever PDF is opened in any browser "
               "it would trigger Print window",
    "category": "Website",
    "version": "1.0.0",
    "sequence": 1,
    "author": "TKOpen",
    "license": "Other proprietary",
    "website": "https://tkopen.com",
    "depends": [],
    "data": [
        'views/ir_actions_report_view.xml',
    ],
    "images": [
        'static/description/banner.png'
    ],
    "application": True,
    "installable": True,
    "auto_install": False,

}
