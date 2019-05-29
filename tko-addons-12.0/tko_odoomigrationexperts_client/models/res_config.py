from odoo import models, fields, api
from os import urandom

class OdooMigrationExpertsConfig(models.TransientModel):
    _inherit = 'res.config.settings'


    migrationexpoerts_token = fields.Char('OdooMigrationExperts TOKEN')

    def generate_token(self):
        return self.set_values()

    @api.multi
    def set_values(self):
        token = urandom(16).hex()
        self.migrationexpoerts_token = token
        super(OdooMigrationExpertsConfig, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("tko_odoomigrationexperts_client.token", token)

    @api.model
    def get_values(self):
        res = super(OdooMigrationExpertsConfig, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            migrationexpoerts_token=ICPSudo.get_param('tko_odoomigrationexperts_client.token'),
        )
        return res
