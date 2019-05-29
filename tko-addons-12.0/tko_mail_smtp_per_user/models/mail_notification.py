# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Notification(models.Model):
    _inherit = 'mail.notification'

    failure_type = fields.Selection(selection_add=[
        ("OUTGOING_MISSING", "Outgoing mail server not found for sender"),
    ])