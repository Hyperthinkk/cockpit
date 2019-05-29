import json

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, ValidationError, Warning
from . import at_constants
from .faturaqui import COPIES


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    at_payment_mechanism = fields.Selection(at_constants.at_payment_mechanisms.items(), 'AT Payment Mechanism',
                                            readonly=True, states={'draft': [('readonly', False)]})
    at_invoice_type = fields.Selection(at_constants.at_invoice_types.items(), 'AT Invoice Type',
                                       compute='_compute_at_invoice_type', store=True, help='Tipo de documento')
    at_self_billing_indicator = fields.Boolean('AT Self Billing Indicator', required=True, default=False,
                                               readonly=True, states={'draft': [('readonly', False)]},
                                               help='Indicador de autofaturação')
    at_cash_vat_scheme_indicator = fields.Boolean('AT Cash VAT Scheme Indicator', required=True, default=False,
                                                  readonly=True, states={'draft': [('readonly', False)]},
                                                  help='Indicador da existência de adesão ao regime de IVA de Caixa')
    at_third_parties_billing_indicator = fields.Boolean('AT Third Parties Billing Indicator', required=True, default=False,
                                                        readonly=True, states={'draft': [('readonly', False)]},
                                                        help='Indicador de faturação emitida '
                                                             'em nome e por conta de terceiros')
    copies = fields.Selection(COPIES, 'Copies', required=True, default=2, states={'draft': [('readonly', False)]})
    server_reference = fields.Char('Server Reference', readonly=True, index=True, copy=False)
    print_url = fields.Char('Print URL', size=1024, copy=False)

    reason_cancel = fields.Char('Cancel Reason', readonly=True, copy=False)
    server_message = fields.Text('Server Message', invisible=True, default='{}', copy=False)

    @api.multi
    @api.depends('type', 'journal_id')
    def _compute_at_invoice_type(self):
        for record in self.filtered(lambda x: x.type in ['out_invoice', 'out_refund']):
            if record.type == 'out_invoice':
                record.at_invoice_type = record.journal_id.at_type_out_invoice
            elif record.type == 'out_refund':
                record.at_invoice_type = 'NC'

    def validate_customer(self):
        error = ''
        if not self.partner_id.vat:
            error += 'Missing VAT. If unknown, please fill in with PT999999990.\n'
        else:
            if not self.partner_id.vat[:2].isalpha():
                error += 'Incorrect VAT. First two characters must be letters of Country Code.\n'
        if not self.partner_id.street:
            error += 'Missing Address Street. If unknown, please fill in with Desconhecido.\n'
        if not self.partner_id.city:
            error += 'Missing Address City. If unknown, please fill in with Desconhecido.\n'
        if not self.partner_id.zip:
            error += 'Missing Address ZIP. If unknown, please fill in with Desconhecido.\n'
        if not self.partner_id.country_id:
            error += 'Missing Address Country. If unknown, please fill in with Desconhecido.\n'
        if error:
            error = 'Customer %s has: \n' % self.partner_id.name + error
            raise ValidationError(_(error))

    def validate_sequence(self):
        error = ''
        if not ' ' in self.journal_id.sequence_id.prefix:
            error += 'Incorrect Journal Sequence.\n'
        if not ' ' in self.journal_id.refund_sequence_id.prefix:
            error += 'Incorrect Journal Refund Sequence.\n'

    def get_amount_eur(self, amount):
        eur = self.env.ref('base.EUR')
        if self.currency_id.id != eur.id:
            date = self._get_currency_rate_date()
            amount = self.currency_id._convert(amount, eur,
                                               self.company_id or self.env.user.company_id,
                                               date or fields.Date.today())
        return abs(amount)

    def get_address_data(self, partner, type):
        address = ', '.join([partner.street,
                            partner.street2 if partner.street2 else ''])
        address_data = {
            '%s_street_name' % type: partner.street,
            '%s_address_detail' % type: address,
            '%s_city' % type: partner.city,
            '%s_postal_code' % type: partner.zip,
            '%s_country' % type: partner.country_id.code,
        }
        if partner.street2:
            address_data.update({'%s_building_number' % type: partner.street2})
        if partner.state_id:
            address_data.update({'%s_region' % type: partner.state_id.name})
        return address_data

    def get_customer_data(self):
        customer_data = {
            'customer_id': self.partner_id.id,  # 4.1.4.14. required
            'customer_account_id': 'Desconhecido',
            'customer_tax_id': self.partner_id.vat[2:],
            'customer_tax_id_country': self.partner_id.vat[:2],
            'customer_company_name': self.partner_id.name,
            'customer_self_billing_indicator': int(self.partner_id.at_self_billing_indicator),
        }
        customer_data.update(self.get_address_data(self.partner_id, 'customer_billing_address'))
        if self.partner_id.phone or self.partner_id.mobile:
            customer_data.update({'customer_telephone': self.partner_id.phone or self.partner_id.mobile})
        if self.partner_id.email:
            customer_data.update({'customer_email': self.partner_id.email})
        if self.partner_id.website:
            customer_data.update({'customer_website': self.partner_id.website})
        return customer_data

    def get_invoice_data(self):
        invoice_data = {
            'internal_reference': self.id,
            'copies': self.copies,
            'internal_code': self.journal_id.code if self.type == 'out_invoice' else self.journal_id.refund_code,
            'series': self.journal_id.series,
            'document_origin': self.journal_id.at_origin,
            'invoice_date': fields.Date.to_string(self.date_invoice),
            'invoice_type': self.at_invoice_type,
            'self_billing_indicator': int(self.at_self_billing_indicator),
            'cash_vat_scheme_indicator': int(self.at_cash_vat_scheme_indicator),
            'third_parties_billing_indicator': int(self.at_third_parties_billing_indicator),
            'source_id': '%d-%s' % (self.env.user.id, self.env.user.login),
            'tax_payable': self.get_amount_eur(self.amount_tax),
            'net_total': self.get_amount_eur(self.amount_untaxed),
            'gross_total': self.get_amount_eur(self.amount_total),
        }
        invoice_data.update(self.get_customer_data())
        if hasattr(self, 'partner_shipping_id'):
            invoice_data.update(self.get_address_data(self.partner_shipping_id, 'ship_to'))
        lines_list = invoice_data.setdefault('lines', [])
        lines = self.invoice_line_ids.filtered(lambda x: not x.display_type)
        lines.validate_line()
        for i, line in enumerate(lines):
            line_data = {
                'line_number': i + 1,  # 4.1.4.19.1. required
                'quantity': line.quantity,  # 4.1.4.19.5. required
                'unit_of_measure': line.uom_id.name,  # 4.1.4.19.6. required
                'unit_price': line.at_unit_price, # 4.1.4.19.7. required
                'tax_point_date': fields.Date.to_string(line.invoice_id.date_invoice),  # or line.invoice_id.tdoc_id.date  # 4.1.4.19.9. required
                'description': line.name,  # 4.1.4.19.11. required
            }
            line_data.update(line.get_product_data())
            if line.invoice_id.type == 'out_refund':
                line_data.update({
                    'references': [{
                        'reference': line.invoice_id.origin,  # 4.1.4.19.10.1.
                        'reason': line.invoice_id.name,  # 4.1.4.19.10.2.
                    }],
                })
            if line.invoice_id.type == 'out_refund':
                line_data.update({
                    'debit_amount': self.get_amount_eur(line.price_subtotal),  # 4.1.4.19.13. required
                })
            elif line.invoice_id.type == 'out_invoice':
                line_data.update({
                    'credit_amount': self.get_amount_eur(line.price_subtotal),  # 4.1.4.19.14. required
                })
            line_data.update(line.get_tax_data())
            lines_list.append(line_data)
        if self.currency_id.name != 'EUR':
            invoice_data.update({
                'currency_code': self.currency_id.name,  # 4.1.4.20.4.1. required
                'currency_amount': abs(self.amount_total_signed),  # 4.1.4.20.4.2. required
                'exchange_rate': self.currency_id.with_context(
                    dict(self._context or {}, date=self.date_invoice)).rate  # 4.1.4.20.4.3. required
            })
        if self.type == 'out_invoice' and self.date_due:
            invoice_data.update({
                'settlement': [{
                    'payment_terms': fields.Date.to_string(self.date_due),  # 4.1.4.20.5.4.
                }],
            })
        if self.at_payment_mechanism:
            invoice_data.update({'payment_mechanism': self.at_payment_mechanism})
        return invoice_data

    def get_status_data(self, status):
        now = fields.Datetime.to_string(fields.Datetime.now())
        status_data = {
            'invoice_status': status,
            'invoice_status_date': now,
            'status_source_id': '%d-%s' % (self.env.user.id, self.env.user.login),
        }
        if status == 'N':
            status_data.update({
                'system_entry_date': now,
            })
        return status_data

    def emit_invoice(self):
        self.validate_customer()
        data = self.get_invoice_data()
        data.update(self.get_status_data('N'))
        response = self.env['faturaqui'].emit(data, 'create', 'invoice')
        if response.get('error'):
            raise AccessError(_('FaturAqui Server Error: %s' % response['error']['message']))
        if response.get('result'):
            result = response['result']
            self.move_id.name = result['number']
            self.server_reference = result['server_reference']
            self.print_url = result['url']
        return True

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for record in self.filtered(lambda x: x.type in ['out_invoice', 'out_refund']):
            record.emit_invoice()
        return res

    @api.multi
    def action_invoice_print(self):
        self.ensure_one()
        if not self.print_url:
            raise Warning('Missing invoice print URL.')
        return {
            'name': 'PDF',
            'type': 'ir.actions.act_url',
            'url': self.print_url,
            'target': 'new',
        }

    @api.multi
    def action_validate_and_print(self):
        self.ensure_one()
        self.action_invoice_open()
        return self.action_invoice_print()

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'cancel' and self.type in ('out_invoice', 'out_refund'):
            return 'tko_faturaqui_client.mt_invoice_cancelled'
        return super(AccountInvoice, self)._track_subtype(init_values)

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        for record in self:
            json_data = {'internal_reference': record.id, 'status_reason': record.reason_cancel}
            json_data.update(self.get_status_data('A'))
            server_message = json.loads(record.server_message)
            if server_message:
                json_data.update({'server_message': server_message})
            response = self.env['faturaqui'].emit(json_data, 'cancel', 'invoice')
            if response.get('error'):
                raise AccessError(_('FaturAqui Server Error: %s' % response['error']['message']))
        return res

    # TODO: Add correct return view (currently returns vendor bill)
    # @api.multi
    # def action_invoice_draft(self):
    #     self.ensure_one()
    #     invoice_copy = self.copy()
    #     if invoice_copy:
    #         context = dict(self.env.context)
    #         context['form_view_initial_mode'] = 'edit'
    #         print(context)
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'account.invoice',
    #             'res_id': invoice_copy.id,
    #             'context': context,
    #         }
    #     return False


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('price_unit', 'discount', 'quantity',
                 'product_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_at_unit_price(self):
        # super(AccountInvoiceLine, self)._compute_price()
        # In EUR, without discounts and taxes
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        digits = dp.get_precision('Product Price')(self.env.cr)[1]
        self.at_unit_price = round(self.invoice_id.get_amount_eur(price), digits)
        self.at_settlement_amount = self.quantity * round(self.price_unit - self.at_unit_price, digits)

    tax0_reason_id = fields.Many2one('account.tax.er', 'Exemption Reason')
    at_unit_price = fields.Float(string='AT Unit Price', digits=dp.get_precision('Product Price'),
                                 compute='_compute_at_unit_price', store=True,
                                 help='Preço unitário deduzido dos descontos '
                                      'de linha e cabeçalho, sem incluir impostos.')
    at_settlement_amount = fields.Float(string='AT Settlement Amount', digits=(16, 2),
                                        compute='_compute_at_unit_price', store=True,
                                        help='Deve refletir todos os descontos concedidos '
                                                        '(a proporção dos descontos globais para esta linha '
                                                        'afetam o valor do campo 4.1.4.20.3. – '
                                                        'Total do documento com impostos (GrossTotal).')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            self.tax0_reason_id = self.product_id.tax0_reason_id
        return res

    @api.onchange('invoice_line_tax_ids')
    def _onchange_invoice_line_tax_ids(self):
        if not self.invoice_line_tax_ids:
            self.tax0_reason_id = False
        else:
            if all(tax_amount for tax_amount in self.invoice_line_tax_ids.mapped('amount')):
                self.tax0_reason_id = False

    @api.multi
    def validate_line(self):
        error = ''
        for record in self:
            line_error = ''
            if not record.quantity:
                line_error += 'Quantity.\n'
            if not record.uom_id:
                line_error += 'Unit of Measure.\n'
            if len(record.invoice_line_tax_ids) != 1:
                line_error += 'Exactly one Tax.\n'
            if not record.invoice_line_tax_ids.amount and not record.tax0_reason_id:
                line_error += 'Tax Exemption Reason.\n'
            if line_error:
                error += 'Invoice line %s must have: \n' % record.name + line_error
        if error:
            raise ValidationError(_(error))

    def get_product_data(self):
        product_data = {
            'product_code': self.product_id.id,
            'product_description': self.product_id.name,
            'product_type': self.product_id.at_product_type,
            'product_number_code': self.product_id.barcode or self.product_id.id,
        }
        if self.product_id and self.product_id.categ_id:
            product_data.update({'product_group': self.product_id.categ_id.name})
        return product_data

    def get_tax_data(self):
        tax = self.invoice_line_tax_ids
        tax_data = {
            'tax_type': tax.at_tax_type,
            'tax_country_region': tax.at_tax_country_region,
            'tax_code': tax.at_tax_code,
            'tax_description': tax.name,
        }
        if tax.amount_type == 'percent':
            tax_data.update({'tax_percentage': tax.amount})
        elif tax.amount_type == 'fixed':
            tax_data.update({'tax_amount': tax.amount})
        if self.tax0_reason_id:
            tax_data.update({
                'tax_exemption_reason': self.tax0_reason_id.name,  # 4.1.4.19.16.
                'tax_exemption_code': self.tax0_reason_id.at_tax0_code,  # 4.1.4.19.17.
            })
        return tax_data
