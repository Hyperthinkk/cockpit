# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################


import uuid
from itertools import groupby
from datetime import datetime, timedelta, date
from werkzeug.urls import url_encode
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
import time


class account_payment(models.Model):
    _inherit = "account.payment"
    
    @api.depends('write_date','write_uid','reconciled_invoice_ids')
    def _compute_invoice_id(self):
        for rec in self:
            for rec_ids in rec.reconciled_invoice_ids:
                if rec.partner_type == 'customer':
                    invoice = self.env['account.invoice'].search([('reference','=',rec.communication)])
                elif rec.partner_type == 'supplier':
                    invoice = self.env['account.invoice'].search([('number','=',rec.communication)])
                if invoice.id == rec_ids.id:
                    rec.invoice_id = rec_ids.id
        
    invoice_id = fields.Many2one('account.invoice', compute='_compute_invoice_id', string="Invoice Number")
    invoice_new = fields.Many2one('account.invoice', related='invoice_id', string="Number New", store=True)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id == self.account_id:
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = line.currency_id or line.company_id.currency_id
                    residual += from_currency._convert(line.amount_residual, self.currency_id, line.company_id, line.date or fields.Date.today())
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False
        self.paid_amount = self.amount_total - self.residual
    
    paid_amount = fields.Float(string="Payments/Credit", compute='_compute_residual')
    new_date_invoice = fields.Date(string='New Invoice Date', related='date_invoice')
    new_date_due = fields.Date(string='New Due Date', related='date_due')
    new_company_id = fields.Many2one('res.company', string='New Company',related='company_id')
    
    
class account_move_line(models.Model):
    _inherit = 'account.move.line'

    stat_report = fields.Boolean(string='Statement Report')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
