from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    at_self_billing_indicator = fields.Boolean('AT Self Billing Indicator', required=True, default=False,
                                               help='Indicador de autofaturação. '
                                                    'Indicador da existência de acordo de autofaturação '
                                                    'entre o cliente e o fornecedor.')

    @api.onchange('vat')
    def _onchange_vat(self):
        if self._origin.total_invoiced and self._origin.vat != 'PT999999990':
            raise ValidationError(_('Cannot change VAT for already invoiced partner'))
