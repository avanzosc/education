# Copyright 2020 Adrian Revilla - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    validate_OK = fields.Boolean(string='Validate OK',
                               default=False, required=True)

    center_id = fields.Many2one(comodel_name="product.product", related='product_id.company_id')

    @api.multi
    def change_value_btn(self):
        self.validate_OK = not(self.validate_OK)




