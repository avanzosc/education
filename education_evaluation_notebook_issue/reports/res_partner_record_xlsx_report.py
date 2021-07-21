# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class EducationGroupXlsx(models.AbstractModel):
    _inherit = "report.education.partner_record_xlsx"

    def __init__(self, pool, cr):
        super().__init__(pool, cr)

    def write_issue_count(self, sheet, row, eval_type, data, cell_format):
        if eval_type == "first":
            column = 3
        elif eval_type == "second":
            column = 4
        elif eval_type == "third":
            column = 5
        elif eval_type == "final":
            column = 6
        else:
            return False
        sheet.write(row, column, data, cell_format)

    def fill_student_subject_data(self, sheet, student, subject, row):
        # observation_obj = self.env["education.notebook.observation"]
        # evaluation_obj = self.env["education.academic_year.evaluation"]
        issues_obj = self.env["school.issue"]
        row = super(EducationGroupXlsx, self).fill_student_subject_data(
            sheet, student, subject, row)
        issues = issues_obj.sudo().search([
            ("academic_year_id.current", "=", True),
            ("student_id", "=", student.id),
            ("education_schedule_id.subject_id", "=", subject.id),
        ])
        if issues:
            sheet.merge_range(
                row, 0, row, 6, _("Issues"), self.format_header_center)
            row += 1
            for issue_type in issues.mapped("school_issue_type_id"):
                sheet.merge_range(
                    row, 0, row, 2, issue_type.display_name,
                    self.format_header_center)
                for eval_type in ["first", "second", "third", "final"]:
                    eval_issues = issues.filtered(
                        lambda i: i.evaluation_id.eval_type == eval_type and
                        i.school_issue_type_id == issue_type)
                    self.write_issue_count(
                        sheet, row, eval_type, len(eval_issues),
                        self.format_border)
                row += 1
        return row
