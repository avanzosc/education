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
        computed='_compute_school_ids', store=True)

    @api.multi
    @api.depends("invoice_line_ids", "invoice_line_ids.validate_ok")
    def _compute_validate_ok(self):
        for record in self:
            record.validate_ok =\
                all(record.mapped("invoice_line_ids.validate_ok"))

    @api.multi
    @api.depends('invoice_lines', 'invoice_lines.school_id')
    def _compute_school_ids(self):
        for invoice in self:
            lines = invoice.invoice_lines.filtered(lambda x: x.school_id and x.invoice_id == self.id)
            schools = lines.mapped('school_id')
            invoice.line_school_ids = [(6, 0, schools.ids)]
