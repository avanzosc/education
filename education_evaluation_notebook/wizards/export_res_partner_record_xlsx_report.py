# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ..models.education_academic_year_evaluation import EVAL_TYPE
from odoo import _, api, fields, models


class ExportPartnerEducationRecordReport(models.TransientModel):
    _name = "report.education.partner_education_record_xlsx.export"
    _description = "Wizard to export partner education records in xlsx"

    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year", string="Academic Year",
        required=True,
        default=lambda self: self.env["education.academic_year"].search([
            ("current", "=", True)], limit=1))
    eval_type = fields.Selection(
        selection=EVAL_TYPE, string="Evaluation Season", default="final",
        required=True)
    partial_mark = fields.Boolean(
        string="Partial Marks", default=False)
    retaken = fields.Boolean(string="Retaken Marks", default=False)
    accumulated = fields.Boolean(
        string="Accumulated", default=False,
        help="If this check is selected, none of the other fields will be "
             "taken into account")

    @api.multi
    def export_xls(self):
        report_name = "education.partner_record_xlsx"
        # if self.accumulated:
        #     report_name = "education.education_record_all_xlsx"
        print_report_name = _("Evaluation Record")
        report = {
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": report_name,
            "print_report_name": print_report_name,
            "context": dict(self.env.context, report_file="group_records"),
            "data": {
                "academic_year_id": self.academic_year_id.id,
                "eval_type": self.eval_type,
                "partial_mark": self.partial_mark,
                "retaken": self.retaken,
            },
        }
        return report
