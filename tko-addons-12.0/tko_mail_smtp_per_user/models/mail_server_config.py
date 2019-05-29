# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import except_orm, UserError
from odoo.tools import ustr

class MailServerConfig(models.Model):
    _name = 'mail.server.config'
    _rec_name = 'login'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = "Mail Server Config"

    login = fields.Char('Login', readonly=True)
    password = fields.Char('Password')

    @api.multi
    def test_smtp_connection(self, smtp_server):
        """ Note: Redefining because it raises warning on success,
        if we raise a warning we can't write in password field"""
        for server in smtp_server:
            smtp = False
            try:
                smtp = smtp_server.connect(mail_server_id=server.id)
                # simulate sending an email from current user's address - without sending it!
                email_from, email_to = self.env.user.email, 'noreply@odoo.com'
                if not email_from:
                    raise UserError(_('Please configure an email on the current user to simulate '
                                      'sending an email message via this outgoing server'))
                # Testing the MAIL FROM step should detect sender filter problems
                (code, repl) = smtp.mail(email_from)
                if code != 250:
                    raise UserError(_('The server refused the sender address (%(email_from)s) '
                                      'with error %(repl)s') % locals())
                # Testing the RCPT TO step should detect most relaying problems
                (code, repl) = smtp.rcpt(email_to)
                if code not in (250, 251):
                    raise UserError(_('The server refused the test recipient (%(email_to)s) '
                                      'with error %(repl)s') % locals())
                # Beginning the DATA step should detect some deferred rejections
                # Can't use self.data() as it would actually send the mail!
                smtp.putcmd("data")
                (code, repl) = smtp.getreply()
                if code != 354:
                    raise UserError(_('The server refused the test connection '
                                      'with error %(repl)s') % locals())
            except UserError as e:
                # let UserErrors (messages) bubble up
                raise e
            except Exception as e:
                raise UserError(_("Connection Test Failed! Here is what we got instead:\n %s") % ustr(e))
            finally:
                try:
                    if smtp:
                        smtp.close()
                except Exception:
                    # ignored, just a consequence of the previous exception
                    pass
        # Return True if everything is okay
        return True


    def update_password(self):

        smtp_server = self.env['ir.mail_server'].search([('smtp_user','=',self.login)])
        if smtp_server:
            # self.env.cr.execute("update ir_mail_server  set smtp_pass='%s'"%self.password)
            smtp_server.write({'smtp_pass' : self.password})
            self.test_smtp_connection(smtp_server)
            self.env.user.notify_success(_(_("Outgoing mail server connection Test Succeeded! Everything seems properly set up!")))
            # unlink config and activities

        fetchmail_server =  self.env['fetchmail.server'].search([('user','=',self.login)])
        if fetchmail_server:
            fetchmail_server.write({'password': self.password})
            try:
                fetchmail_server.connect()
                fetchmail_server.write({'state': 'done'})
                self.env.user.notify_success(_("Incoming mail server Connection Succeeded! Everything seems properly set up!"))
            except:
                self.env.user.notify_danger(_("Incoming mail server Authentication Failure!"))
        #unlink record and activities
        self.sudo().unlink()
        return True


    def create_notification(self, server= False, type='outgoing'):
        user = self.env.user
        # user = self.env.user.search([('partner_id', '=', mail.author_id.id)])
        try:
            activity_id = self.env.ref('mail.mail_activity_data_warning').id
        except:
            activity_id = False
        doc = self.env['mail.server.config'].search([('login', '=', user.login)], limit=1)
        if not doc:
            doc = self.env['mail.server.config'].create({'login': user.login,
                                                         'user_id': user.id})
        if type == 'outgoing':
            summary = 'SMTP Failure'
            note = 'Please Fix your outgoing mail server %s' % server.name
        else:
            summary = 'Authentication Failure'
            note = 'Please Fix your Incoming mail server %s' % server.name

        activity = self.env['mail.activity'].sudo().create({'activity_type_id': activity_id,
                                                 'date_deadline': fields.Date.today(),
                                                 'summary': summary,
                                                 'note': note,
                                                 'user_id': user.id,
                                                 'res_model': 'mail.server.config',
                                                 'res_id': doc.id,
                                                 'res_model_id': self.env['ir.model']._get('mail.server.config').id
                                                 })
        return activity