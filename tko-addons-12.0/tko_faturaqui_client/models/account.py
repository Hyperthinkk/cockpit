from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from .faturaqui import ORIGINS


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    at_type_out_invoice = fields.Selection([
        ('FT', 'Invoice'),
        ('FS', 'Simplified Invoice'),
    ], 'AT Invoice Type')
    at_origin = fields.Selection(ORIGINS, 'AT Invoice Origin', default='system')
    code = fields.Char(string='Short Code', size=25, required=True,
                       help='The journal entries of this journal will be named using this code.')
    refund_code = fields.Char(string='Refund Code', size=25,
                              help='The refund entries of this journal will be named using this code.')
    series = fields.Char(string='Series', compute='_compute_series', store=True)

    def _get_code_series(self, prefix):
        split_by = ' ' if ' ' in prefix else '/'
        split = prefix.split(split_by, 1)
        code = split[0]
        series = split[1].strip('/')
        return code, series

    @api.multi
    @api.depends('sequence_id')
    def _compute_series(self):
        for record in self.filtered(lambda x: x.type == 'sale'):
            if record.sequence_id:
                prefix, _ = record.sequence_id._get_prefix_suffix()
                code, series = self._get_code_series(prefix)
                record.series = series

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'sale':
            self.refund_sequence = True

    @api.multi
    @api.constrains('refund_sequence')
    def _check_refund_sequence(self):
        for record in self.filtered(lambda x: x.type == 'sale'):
            if not record.refund_sequence:
                raise ValidationError(_('Invoice Series must have a Dedicated Credit Note Sequence.'))

    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code
        if refund:
            prefix = 'R' + code
        return prefix + ' %(range_year)s/'

    @api.model
    def update_customer_invoices(self):
        for record in self.search([]):
            if record.type == 'sale':
                record.refund_sequence = True
                if record.name == 'Customer Invoices':
                    record.at_type_out_invoice = 'FT'
                    record.code = 'FT'
                    record.refund_code = 'RFT'
