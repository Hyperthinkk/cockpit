# -*- coding: utf-8 -*-
import odoo
from odoo import api, models
from odoo import SUPERUSER_ID
from odoo.exceptions import Warning

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        res = super(MailComposeMessage, self).default_get(fields)
        context = self.env.context
        token = server_url = partner = ''
        ICPSudo = self.env['ir.config_parameter'].sudo()
        PartnerSudo = self.env['res.partner'].sudo()
        UserSudo = self.env['res.users'].sudo()
        CompanySudo = self.env['res.company'].sudo()
        company = CompanySudo.search([], limit=1,  order='id asc')
        if context.get('odoomigrationexperts', False) and context.get('active_model', False) == 'res.config.settings':
            active_model = 'res.config.settings'
            active_id = context.get('active_id')

            server_url = ICPSudo.get_param('web.base.url')
            if active_id:
                token = self.env['res.config.settings'].browse(active_id).migrationexpoerts_token
                if not token:
                    raise Warning("Please generate a Token before sending an email!")
            partner = PartnerSudo.search([('email', '=', 'info@odoomigrationexperts.com')], limit=1)
            if not partner:
                partner = PartnerSudo.create({'name': 'OdooMigrationExperts.com',
                                              'email': 'info@odoomigrationexperts.com',
                                              'is_supplier': True})
        if partner:
            superuser= UserSudo.search([('id','=',SUPERUSER_ID)])
            body = '''
            <p>Hello OdooMigrationExperts,</p>
            <p>As per the instructions we have generated the token and would like to share the following information&nbsp;with you to start the database migration process .</p>
            <ul>
            <li style="font-size: 14px;"><strong>Server URL: </strong>%s</li>
            <li style="font-size: 14px;"><strong>Database Name:&nbsp;</strong>%s</li>
            <li style="font-size: 14px;"><strong>SuperUser Login: </strong>%s</li>
            <li style="font-size: 14px;"><strong>OdooMigrationExpert Token: </strong>%s</li>
            <li style="font-size: 14px;"><strong>Current Odoo Version: </strong> %s</li>
            <li style="font-size: 14px;"><strong>Target Odoo Version: </strong> </li>
            <li style="font-size: 14px;"><strong>Contact Email: </strong> %s</li>
            <li style="font-size: 14px;"><strong>Contact Number: </strong> %s</li>
            <li style="font-size: 14px;"><strong>Any further Queries?: </strong> </li>
            </ul>
            <p>Thank you.</p>
            
            ''' %(server_url, self.env.cr.dbname,superuser.login, token, odoo.release.version,company.phone, company.email)
            res['partner_ids'] = [(6, 0, [partner.id])]
            res['subject'] = 'OdooMigrationExperts Database Migration'
            res['body'] = body
        return res
