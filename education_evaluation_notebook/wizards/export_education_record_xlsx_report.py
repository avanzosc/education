# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ..models.education_academic_year_evaluation import EVAL_TYPE
from odoo import _, api, fields, models


class ExportEducationRecordReport(models.TransientModel):
    _name = "report.education.education_record_xlsx.export"
    _description = "Wizard to export education records in xlsx"

    eval_type = fields.Selection(
        selection=EVAL_TYPE, string="Evaluation Season", default="final",
        required=True)
    partial_mark = fields.Boolean(
        string="Partial Marks", default=False)

    @api.multi
    def export_xls(self):
        report_name = "education.education_record_xlsx"
        print_report_name = _("Evaluation Record")
        report = {
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": report_name,
            "print_report_name": print_report_name,
            "context": dict(self.env.context, report_file="group_records"),
            "data": {
                "eval_type": self.eval_type,
                "partial_mark": self.partial_mark,
            },
        }
        return report
