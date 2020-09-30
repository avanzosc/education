# Copyright 2020 Adrian Revilla - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    validate_OK = fields.Boolean(compute='check_value', string='Validate OK',
                                 store=True, compute_sudo=True)

    @api.one
    @api.depends("invoice_line_ids.validate_OK")
    def check_value(self):
        self.validate_OK = all(self.invoice_line_ids.mapped("validate_OK"))

