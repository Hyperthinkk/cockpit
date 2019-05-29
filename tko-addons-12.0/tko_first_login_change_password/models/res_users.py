from odoo import api, fields, models, _
from odoo.addons.auth_signup.models.res_partner import now


class Users(models.Model):
    _inherit = 'res.users'

    @api.multi
    def _first_login(self):
        self.ensure_one()
        return len(self.log_ids) == 1

    @api.multi
    def action_signup_prepare(self):
        for record in self:
            record.mapped('partner_id').signup_prepare(signup_type='reset', expiration=now(days=+1))
