# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SchoolIssue(models.Model):
    _inherit = "school.issue"

    evaluation_id = fields.Many2one(
        comodel_name="education.academic_year.evaluation", string="Evaluation",
        compute="_compute_academic_year_evaluation", store=True)

    @api.depends("academic_year_id", "school_id", "student_course_id")
    def _compute_academic_year_evaluation(self):
        evaluation_obj = self.env["education.academic_year.evaluation"]
        for issue in self:
            issue.evaluation_id = evaluation_obj.search([
                ("academic_year_id", "=", issue.academic_year_id.id),
                ("center_id", "=", issue.school_id.id),
                ("course_id", "=", issue.student_course_id.id),
                ("date_start", "<=", issue.issue_date),
                ("date_end", ">=", issue.issue_date),
            ], limit=1)
