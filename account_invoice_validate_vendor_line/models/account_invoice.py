# Copyright 2020 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    validate_ok = fields.Boolean(compute='_compute_validate_ok',
                                 string='Validated',
                                 store=True, compute_sudo=True)
    line_school_ids = fields.Many2many(
        comodel_name='res.partner', string='Schools',
        relation='account_invoice_school',
        column1='invoice_id', column2='school_id',
        compute='_compute_school_ids', store=True)

    @api.multi
    @api.depends("invoice_line_ids", "invoice_line_ids.validate_ok")
    def _compute_validate_ok(self):
        for record in self:
            record.validate_ok =\
                all(record.mapped("invoice_line_ids.validate_ok"))

    @api.multi
    @api.depends('invoice_line_ids', 'invoice_line_ids.product_center_id')
    def _compute_school_ids(self):
        for invoice in self:
            invoice.line_school_ids = invoice.mapped(
                'invoice_line_ids.product_center_id')
