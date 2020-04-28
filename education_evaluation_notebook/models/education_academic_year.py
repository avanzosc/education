# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import RedirectWarning


class EducationAcademicYear(models.Model):
    _inherit = "education.academic_year"

    @api.multi
    def create_evaluations(
            self, center, course, evaluation_number=1, final_evaluation=False):
        self.ensure_one()
        evaluation_obj = self.env["education.academic_year.evaluation"]
        eval_type = evaluation_obj.fields_get(
            allfields=["eval_type"])["eval_type"]["selection"]
        if not self.date_start or not self.date_end:
            msg = _("Academic year must have defined start and end dates.")
            action = self.env.ref(
                "education.action_education_academic_year")
            action_msg = _("Configure Academic Year")
            raise RedirectWarning(msg, action.id, action_msg)
        vals = {
            "academic_year_id": self.id,
            "course_id": course.id,
            "center_id": center.id,
            "date_start": self.date_start,
            "date_end": self.date_end,
        }
        for i in range(0, evaluation_number):
            vals.update({
                "name": "{} [{}]".format(
                    course.description, eval_type[i][1]),
                "eval_type": eval_type[i][0],
            })
            evaluation_obj.find_or_create_evaluation(vals)
        if final_evaluation:
            vals.update({
                "name": "{} [Final]".format(course.description),
                "eval_type": "final",
            })
            evaluation_obj.find_or_create_evaluation(vals)
