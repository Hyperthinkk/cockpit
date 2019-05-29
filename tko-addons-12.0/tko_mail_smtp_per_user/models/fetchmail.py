# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import except_orm, UserError
import logging
_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    """Incoming POP/IMAP mail server account"""

    _inherit = 'fetchmail.server'

    @api.multi
    def fetch_mail(self):
        for server in self:
            try:
                server.connect()
                self.env.user.notify_success(_(_("Connection Test Succeeded! Everything seems properly set up!")))
            except:
                self.env.user.notify_danger(_("Incoming mail server Authentication Failure!"))
                self.env['mail.server.config'].create_notification(server, 'incoming')
        return super(FetchmailServer, self).fetch_mail()