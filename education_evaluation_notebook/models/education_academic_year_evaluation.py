# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationAcademicYearEvaluation(models.Model):
    _inherit = "education.academic_year.evaluation"

    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain=[("educational_category", "=", "school")])
    course_id = fields.Many2one(
        comodel_name="education.course", string="Course")
    eval_type = fields.Selection(selection=[
        ("first", "First"),
        ("second", "Second"),
        ("third", "Third"),
        ("final", "Final")],
        string="Evaluation Season", default="final", required=True)

    @api.multi
    def find_or_create_evaluation(self, values):
        evaluation = self.search([
            ("academic_year_id", "=", values.get("academic_year_id")),
            ("center_id", "=", values.get("center_id")),
            ("course_id", "=", values.get("course_id")),
            ("eval_type", "=", values.get("eval_type"))
        ])
        if not evaluation:
            evaluation = self.create(values)
        return evaluation

    _sql_constraints = [
        ('name_unique', 'unique(name, academic_year_id, center_id, course_id)',
         'Evaluation name must be unique!'),
    ]
