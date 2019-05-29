from odoo import api, fields, models, _
from . import at_constants


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    at_product_type = fields.Selection(at_constants.at_product_types.items(), 'AT Product Type',
                                       help='Indicador de produto ou serviço')
    tax0_reason_id = fields.Many2one('account.tax.er', 'Tax Exemption Reason', copy=False)
    has_tax0 = fields.Boolean('Needs Tax Exemption Reason', compute='_compute_has_tax0')

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'consu':
            at_product_type = 'P'
        elif self.type == 'service':
            at_product_type = 'S'
        else:
            at_product_type = 'O'
        self.at_product_type = at_product_type

    @api.multi
    @api.depends('taxes_id')
    def _compute_has_tax0(self):
        for record in self:
            if any(not tax_amount for tax_amount in record.taxes_id.mapped('amount') if record.taxes_id):
                record.has_tax0 = True
                record.tax0_reason_id = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_tax0 = fields.Boolean('Needs Tax Exemption Reason', compute='_compute_has_tax0')

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'consu':
            at_product_type = 'P'
        elif self.type == 'service':
            at_product_type = 'S'
        else:
            at_product_type = 'O'
        self.at_product_type = at_product_type

    @api.multi
    @api.depends('taxes_id')
    def _compute_has_tax0(self):
        for record in self:
            if any(not tax_amount for tax_amount in record.taxes_id.mapped('amount') if record.taxes_id):
                record.has_tax0 = True
                record.tax0_reason_id = False
