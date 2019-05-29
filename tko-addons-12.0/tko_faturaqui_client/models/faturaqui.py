import json
import os
import urllib.request

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


COPIES = [
    (2, _('Duplicated')),
    (3, _('Triplicated')),
    (4, _('Quadruplicated')),
]

ORIGINS = [
    ('system', _('System')),
    # 'manual': 'Manual',
    # 'recovery': 'Recovery',
    # 'other': 'Other',
]

months = [
    ('01', _('January')),
    ('02', _('February')),
    ('03', _('March')),
    ('04', _('April')),
    ('05', _('May')),
    ('06', _('June')),
    ('07', _('July')),
    ('08', _('August')),
    ('09', _('September')),
    ('10', _('October')),
    ('11', _('November')),
    ('12', _('December')),
]


class Faturaqui(models.Model):
    _name = 'faturaqui'
    _description = 'FaturAqui'

    name = fields.Char('Software Name', required=True, readonly=True)
    version = fields.Char('Software Version', required=True, readonly=True)
    software_certificate_number = fields.Char('Software Certificate Number', required=True, readonly=True)

    server_url = fields.Char('Server URL')  # To make required need to provide default
    client_token = fields.Char('Client Token')
    use_webservice = fields.Boolean('Use Webservice', default=False)

    @api.model
    def get_main(self):
        main = self.env.ref('tko_faturaqui_client.faturaqui_main')
        if not main.server_url:
            raise UserError(_(
                'Cannot find FaturAqui Server URL. Please update in Invoicing/Configuration/FaturAqui/Information.'))
        if not main.client_token:
            raise UserError(_(
                'Cannot find FaturAqui Client Token. Please update in Invoicing/Configuration/FaturAqui/Information.'))
        return main

    @api.model
    def emit(self, json_data, action, destination):
        main = self.get_main()
        json_data.update({'client_token': main.client_token})
        url = '%s/faturaqui/1.0/%s/%s' % (main.server_url, action.upper(), destination.upper())
        jsondataasbytes = json.dumps(json_data).encode('utf-8')  # needs to be bytes
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Content-Length', len(jsondataasbytes))
        response = urllib.request.urlopen(req, jsondataasbytes)
        string = response.read().decode('utf-8')
        result = json.loads(string)['result']
        return result

    def log(self, document_sudo, action):
        now = fields.Datetime.to_string(fields.Datetime.now())
        user = '%d-%s' % (self.env.user.id, self.env.user.login)
        server_message = json.loads(document_sudo.server_message)
        server_message.update({
            action: {
                'date': now,
                'user': user,
            }
        })
        document_sudo.server_message = json.dumps(server_message)
        if action == 'original':
            msg = _('Confirmed having kept the invoice\'s original')
        document_sudo.message_post(body=msg, message_type='comment', subtype='mail.mt_note')
        return True


class FaturaquiSaft(models.Model):
    _name = 'faturaqui.saft'
    _description = 'FaturAqui SAF-T'

    @api.model
    def _default_month(self):
        month = '%02d' % fields.Date.from_string(fields.Date.context_today(self)).month
        return month

    @api.model
    def _default_year(self):
        return str(fields.Date.from_string(fields.Date.context_today(self)).year)

    name = fields.Char(string='Name', required=True, readonly=True)
    type = fields.Selection([('m', 'Monthly'),
                             ('a', 'Annual')], 'Type', required=True, readonly=True)
    month = fields.Selection(months, 'Month', default=_default_month)
    year = fields.Char('Year', default=_default_year)

    file = fields.Binary('File', readonly=True, copy=False)
    filename = fields.Char('Filename')

    def get_saft_data(self):
        saft_data = {
            'year': self.year,
        }
        if self.type == 'm':
            saft_data.update({'month': self.month})
        return saft_data

    def generate_file(self):
        data = self.get_saft_data()
        response = self.env['faturaqui'].emit(data, 'create', 'saft')
        if response.get('error'):
            raise AccessError(_('FaturAqui Server Error: %s' % response['error']['message']))
        if response.get('result'):
            result = response['result']
            self.file = result['file']
            self.filename = result['filename']
        return True

    @api.constrains('year')
    def _check_year(self):
        if not self.year.isdigit():
            raise ValidationError(_('Cannot use this year.'))
