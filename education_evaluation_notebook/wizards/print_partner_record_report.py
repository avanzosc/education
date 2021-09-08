# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ..models.education_academic_year_evaluation import EVAL_TYPE
from odoo import api, fields, models


class ExportEducationRecordReport(models.TransientModel):
    _name = "print.partner.record.report"
    _description = "Wizard to print Report Card Report"

    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year", string="Academic Year",
        required=True,
        default=lambda self: self.env["education.academic_year"].search([
            ("current", "=", True)], limit=1))
    eval_type = fields.Selection(
        selection=EVAL_TYPE, string="Evaluation Season", default="final",
        required=True)

    @api.multi
    def print_report(self):
        partners = self.env[self.env.context.get("active_model")].browse(
            self.env.context.get("active_ids"))
        [data] = self.read()
        datas = {
            "ids": self.env.context.get("active_ids"),
            "model": self.env.context.get("active_model"),
            "form": data,
        }
        return self.env.ref(
            "education_evaluation_notebook.education_partner_record"
        ).with_context(from_transient_model=True).report_action(
            partners, data=datas, config=False)
