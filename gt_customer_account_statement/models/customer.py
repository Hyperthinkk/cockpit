# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################


import uuid
from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
import time

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    ########### Customer Account Statement And Payment ###############

    @api.depends('filter_by','period_from','period_to' )
    def _compute_cus_account_ids(self):
        for partner in self:
            if partner.filter_by != True:
                partner.cus_account_ids = self.env['account.invoice'].search([
                    ('partner_id','=',partner.id),
                    ('type','=','out_invoice'),])
            
            if partner.filter_by != False:    
                partner.cus_account_ids = self.env['account.invoice'].search([
                    ('partner_id','=',partner.id),
                    ('type','=','out_invoice'),
                    ('new_date_invoice', '>=', partner.period_from),
                    ('new_date_invoice', '<=', partner.period_to),
                ])
                d1 = partner.period_from
                d2 = partner.period_to
                partner.ageing_length = (d2-d1).days
                
    @api.depends('cus_account_ids' )
    def _compute_cus_payment_ids(self):
        ids = []
        for partner in self:
            for rec_ids in partner.cus_account_ids:
                ids.append(rec_ids.id)
            if partner.filter_by != True:
                partner.cus_payment_ids = self.env['account.payment'].search([
                    ('partner_id','=',partner.id),
                    ('partner_type','=','customer'),
                    ('invoice_new', 'in', ids),
                    ])
            
            if partner.filter_by != False:    
                partner.cus_payment_ids = self.env['account.payment'].search([
                    ('partner_id','=',partner.id),
                    ('partner_type','=','customer'),
                    ('invoice_new', 'in', ids),
                ])
    
    ########### Customer Overdue Statement And Payment ###############
    
    @api.depends('filter_by','period_from','period_to' )
    def _compute_cus_overdue_ids(self):
        today = fields.Date.today()
        for partner in self:
            if partner.filter_by != True:
                partner.cus_overdue_ids = self.env['account.invoice'].search([
                    ('date_due','<=',today),
                    ('partner_id','=',partner.id),
                    ('type','=','out_invoice'),
                    ('residual', '>', 0),])
            
            if partner.filter_by != False:    
                partner.cus_overdue_ids = self.env['account.invoice'].search([
                    ('date_due','<=',today),
                    ('partner_id','=',partner.id),
                    ('type','=','out_invoice'),
                    ('new_date_invoice', '>=', partner.period_from),
                    ('new_date_invoice', '<=', partner.period_to),
                    ('residual', '>', 0),
                ])
                
    @api.depends('cus_overdue_ids' )
    def _compute_cus_overdue_payment_ids(self):
        ids = []
        for partner in self:
            for rec_ids in partner.cus_overdue_ids:
                ids.append(rec_ids.id)
            if partner.filter_by != True:
                partner.cus_overdue_payment_ids = self.env['account.payment'].search([
                    ('partner_id','=',partner.id),
                    ('partner_type','=','customer'),
                    ('invoice_new', 'in', ids),
                    ])
            
            if partner.filter_by != False:    
                partner.cus_overdue_payment_ids = self.env['account.payment'].search([
                    ('partner_id','=',partner.id),
                    ('partner_type','=','customer'),
                    ('invoice_new', 'in', ids),
                ])
    
    cus_overdue_statement = fields.Boolean(string='Customer Over Due Statement', default=False)
    customer_statement = fields.Boolean(string='Customer Statement', default=True)
    
    cus_account_ids = fields.One2many('account.invoice', compute='_compute_cus_account_ids', string="Customer Statements")
    cus_payment_ids = fields.One2many('account.payment', compute='_compute_cus_payment_ids', string="Customer Payments")
    cus_overdue_ids = fields.One2many('account.invoice', compute='_compute_cus_overdue_ids', string="Customer Overdue Statements")
    cus_overdue_payment_ids = fields.One2many('account.payment', compute='_compute_cus_overdue_payment_ids', string="Customer Overdue Payments")
    period_from = fields.Date(string='From', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT))
    period_to = fields.Date(string='To', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT))
    ageing_length = fields.Integer('Days Length' , compute='_compute_cus_account_ids', default= 30, readonly=False, store=True)
    filter_by = fields.Boolean(string='Filter By', default=False)
    
    ####################### Customer Account Statement Days Wise ###########################
    
    def get_cus_total_0_30(self):
        totals = 0
        for total in self.cus_account_ids:
            today = fields.Date.today()
            zero_30 = today - timedelta(days=30)
            if total.new_date_invoice > zero_30:
                totals += total.residual
        return totals
    
    def get_cus_total_30_60(self):
        totals = 0
        for total in self.cus_account_ids:
            today = fields.Date.today()
            zero_30 = today - timedelta(days=30)
            thirty_60 = today - timedelta(days=60)
            if total.new_date_invoice <= zero_30 and total.new_date_invoice > thirty_60:
                totals += total.residual
        return totals
    
    def get_cus_total_60_90(self):
        totals = 0
        for total in self.cus_account_ids:
            today = fields.Date.today()
            zero_60 = today - timedelta(days=60)
            sixty_90 = today - timedelta(days=90)
            if total.new_date_invoice <= zero_60 and total.new_date_invoice > sixty_90:
                totals += total.residual
        return totals
    
    def get_cus_total_90_plus(self):
        totals = 0
        for total in self.cus_account_ids:
            today = fields.Date.today()
            zero_90 = today - timedelta(days=90)
            if total.new_date_invoice <= zero_90:
                totals += total.residual
        return totals
    
    def get_cus_total(self):
        totals = 0
        for total in self.cus_account_ids:
            totals += total.residual
        return totals
    
    ####################### Customer Overdue Statement Days Wise ###########################
    
    def get_cus_overdue_total_0_30(self):
        totals = 0
        for total in self.cus_overdue_ids:
            first = fields.Date.today()
            zero_30 = first - timedelta(days=30)
            if total.new_date_invoice > zero_30:
                totals += total.residual
        return totals
    
    def get_cus_overdue_total_30_60(self):
        totals = 0
        for total in self.cus_overdue_ids:
            first = fields.Date.today()
            zero_30 = first - timedelta(days=30)
            thirty_60 = first - timedelta(days=60)
            if total.new_date_invoice <= zero_30 and total.new_date_invoice > thirty_60:
                totals += total.residual
        return totals
    
    def get_cus_overdue_total_60_90(self):
        totals = 0
        for total in self.cus_overdue_ids:
            first = fields.Date.today()
            zero_60 = first - timedelta(days=60)
            sixty_90 = first - timedelta(days=90)
            if total.new_date_invoice <= zero_60 and total.new_date_invoice > sixty_90:
                totals += total.residual
        return totals
    
    def get_cus_overdue_total_90_plus(self):
        totals = 0
        for total in self.cus_overdue_ids:
            first = fields.Date.today()
            zero_90 = first - timedelta(days=90)
            if total.new_date_invoice <= zero_90:
                totals += total.residual
        return totals
    
    def get_cus_overdue_total(self):
        totals = 0
        for total in self.cus_overdue_ids:
            totals += total.residual
        return totals
    
    def get_cus_residual(self, a):
        return a.amount_total - a.paid_amount
    
    def get_cus_paid_amount(self, a):
        return a.paid_amount
    
    def get_cus_overdue_residual(self, a):
        return a.amount_total - a.paid_amount
    
    def get_cus_overdue_paid_amount(self, a):
        return a.paid_amount
    
    @api.multi
    def action_cus_overdue_statement(self):
        self.write({'cus_overdue_statement': True, 'customer_statement': False})
        return True

    @api.multi
    def action_customer_statement(self):
        self.write({'customer_statement': True, 'cus_overdue_statement': False})
        return True
    
    @api.multi
    def action_customer_statement_print(self):
        if self.period_from > self.period_to:
            raise UserError(_('The start date must be anterior to the end date.'))
        return self.env.ref('gt_customer_account_statement.print_customer_statement_report').report_action(self)

    @api.multi
    def action_customer_statement_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('gt_customer_account_statement', 'email_template_customer_statements')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        
        ctx = dict()
        ctx.update({
            'default_model': 'res.partner',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return True
    
    @api.multi
    def action_cus_overdue_statement_print(self):
        if self.period_from > self.period_to:
            raise UserError(_('The start date must be anterior to the end date.'))
        return self.env.ref('gt_customer_account_statement.print_customer_overdue_statement_report').report_action(self)
    
    
    @api.multi
    def action_cus_overdue_statement_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('gt_customer_account_statement', 'email_template_customer_overdue_statements')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'res.partner',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return True
    
    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    