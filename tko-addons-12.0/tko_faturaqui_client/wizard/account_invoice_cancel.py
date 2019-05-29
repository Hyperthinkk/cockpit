from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoiceCancel(models.TransientModel):
    _name = 'account.invoice.cancel'
    _description = 'Cancel Invoice'

    reason = fields.Char(string='Reason', required=True)
    original_kept = fields.Boolean(string='Original Kept', required=True, default=False)

    @api.multi
    def cancel_invoice(self):
        inv_obj = self.env['account.invoice']
        faturaqui_obj =self.env['faturaqui']
        context = dict(self._context or {})
        for form in self:
            if not form.original_kept:
                raise UserError(_('Cannot cancel an invoice if the user hasn\'t declared that they have the original.'))
            for inv in inv_obj.browse(context.get('active_ids')):
                faturaqui_obj.log(inv, 'original')
                inv.reason_cancel = form.reason
                inv.action_cancel()
        return True
