# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.education_evaluation_notebook.models.\
    education_academic_year_evaluation import EVAL_TYPE


class ExportEducationScheduleRecordReport(models.TransientModel):
    _name = "report.education.schedule.record.export"
    _description = "Wizard to print Edu. Schedule Records Report"

    mark_type = fields.Selection(string="Mark", selection=[
        ('provisional', 'Provisional'),
        ('final', 'Final')
    ], default="final", required=True)
    eval_type = fields.Selection(
        selection=EVAL_TYPE, string="Evaluation Season", default="final",
        required=True)

    @api.multi
    def export_xls(self):
        self.ensure_one()
        schedule = self.env['education.schedule'].browse(
            self.env.context.get("active_ids"))
        datas = {
            "schedule": schedule.id,
            "mark_type": self.mark_type,
            "eval_type": self.eval_type
        }
        report = {
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": "education_schedule.academic_record_xlsx",
            "print_report_name": "Schedule_records",
            "context": dict(self.env.context, report_file="group_records"),
            "data": datas
        }
        return report
