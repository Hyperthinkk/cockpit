from odoo import api, fields, models, _


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    # Removed 'refund' option
    filter_refund = fields.Selection([
        ('cancel', 'Cancel: create credit note and reconcile'),
        ('modify', 'Modify: create credit note, reconcile and create a new draft invoice')
    ], default='cancel', string='Refund Method', required=True, help='Refund base on this type. You can not Modify and Cancel if the invoice is already reconciled')
