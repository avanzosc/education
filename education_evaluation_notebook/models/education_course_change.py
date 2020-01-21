# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class EducationCourseChange(models.Model):
    _inherit = "education.course.change"

    @api.model
    def _get_selection_eval_type(self):
        return self.env["education.academic_year.evaluation"].fields_get(
            allfields=["eval_type"])["eval_type"]["selection"]

    @api.multi
    def create_evaluations(self, evaluation_number=1, academic_year=False):
        eval_type = self._get_selection_eval_type()
        academic_year_obj = self.env["education.academic_year"]
        evaluation_obj = self.env["education.academic_year.evaluation"]
        academic_year = (academic_year or
                         academic_year_obj.search([("current", "=", True)]))
        if not academic_year:
            return
        for course_change in self:
            vals = {
                "academic_year_id": academic_year.id,
                "course_id": course_change.course_id.id,
                "center_id": course_change.school_id.id,
                "date_start": academic_year.date_start,
                "date_end": academic_year.date_end,
            }
            for i in range(0, evaluation_number):
                vals.update({
                    "name": eval_type[i][1],
                    "eval_type": eval_type[i][0],
                })
                evaluation_obj.find_or_create_evaluation(vals)
