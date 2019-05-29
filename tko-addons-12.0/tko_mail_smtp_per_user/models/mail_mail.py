# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api,_
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import logging
_logger = logging.getLogger(__name__)

class ir_mail_server(models.Model):
    _inherit = 'ir.mail_server'

    ## Replace the weired Return-Path like <bounce+35-crm.lead-31@domain.com> with email_from
    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
                    attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
                    body_alternative=None, subtype_alternative='plain'):
        try:
            headers.update({'Return-Path' : extract_rfc2822_addresses(email_from)[-1]})
        except:
            _logger.error("Couldn't compute  Return-Path for %s!" %email_from)
        return super(ir_mail_server, self).build_email(email_from, email_to, subject, body, email_cc=email_cc, email_bcc=email_bcc, reply_to=reply_to,
                    attachments=attachments, message_id=message_id, references=references, object_id=object_id, subtype=subtype, headers=headers,
                    body_alternative=body_alternative, subtype_alternative=subtype_alternative)


class mail_mail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        for email in self:
            from_rfc2822 = extract_rfc2822_addresses(email.email_from)[-1]
            outgoing_mail_server = self.env['ir.mail_server'].search([('smtp_user', '=', from_rfc2822)], limit=1)
            if len(outgoing_mail_server):
                email.write({'mail_server_id': outgoing_mail_server.id,
                             'reply_to': email.email_from, })
            else:
                failure_reason = "No outgoing mail server found for  %s !" % from_rfc2822
                email.write({'state': 'exception', 'failure_reason': failure_reason})
                email._postprocess_sent_message(success_pids=[], failure_type='OUTGOING_MISSING')
                _logger.error("No outgoing server found for  %s !" % from_rfc2822)
                return True

        return super(mail_mail, self).send(auto_commit=auto_commit, raise_exception=raise_exception)

    @api.multi
    def _postprocess_sent_message(self, success_pids, failure_reason=False, failure_type=None):
        result = super(mail_mail, self)._postprocess_sent_message(success_pids, failure_reason=failure_reason, failure_type= failure_type)
        for mail in self:
            if failure_type == 'SMTP':
                self.env['mail.server.config'].create_notification(mail.mail_server_id, 'outgoing')
        return result



