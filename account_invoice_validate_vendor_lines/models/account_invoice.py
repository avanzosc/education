# Copyright 2020 Adrian Revilla - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    validate_OK = fields.Boolean(compute='check_value', string='Validate OK')

    @api.one
    def check_value(self):
        self.validate_OK = all(self.invoice_line_ids.mapped("validate_OK"))

    @api.multi
    def filter_validate_ok(self):
        self.validate_OK = not (self.validate_OK)

    @api.multi
    def filter_validate_nok(self):
        self.validate_OK = not (self.validate_OK)
