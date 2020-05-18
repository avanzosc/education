# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationCourseChange(models.Model):
    _inherit = "education.course.change"

    eval_count = fields.Integer(compute="_compute_eval_count")
    next_eval_count = fields.Integer(compute="_compute_eval_count")

    @api.multi
    def _get_academic_years(self):
        current_year = self.env["education.academic_year"].search([
            ("current", "=", True),
        ])
        next_year = current_year._get_next() if current_year else False
        return current_year, next_year

    @api.multi
    def _get_evaluations(self, academic_year, school_id, course_id):
        if not academic_year:
            return self.env["education.academic_year.evaluation"]
        return academic_year.evaluation_ids.filtered(
            lambda e: e.center_id == school_id and e.course_id == course_id)

    @api.depends("next_school_id", "next_course_id")
    def _compute_eval_count(self):
        current_year, next_year = self._get_academic_years()
        for record in self:
            school_id = record.next_school_id
            course_id = record.next_course_id
            record.eval_count = len(
                self._get_evaluations(current_year, school_id, course_id))
            record.next_eval_count = len(
                self._get_evaluations(next_year, school_id, course_id))

    @api.multi
    def button_open_current_evaluations(self):
        current_year, next_year = self._get_academic_years()
        action = self.env.ref(
            "education.action_education_academic_year_evaluation")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("academic_year_id", "=", current_year.id),
             ("center_id", "=", self.next_school_id.id),
             ("course_id", "=", self.next_course_id.id)],
            safe_eval(action.domain or "[]")
        ])
        context = safe_eval(action.context or "{}")
        context.update({
            "default_academic_year_id": current_year.id,
            "default_center_id": self.next_school_id.id,
            "default_course_id": self.next_course_id.id,
        })
        action_dict.update({
            "domain": domain,
            "context": context,
        })
        return action_dict

    @api.multi
    def button_open_next_evaluations(self):
        current_year, next_year = self._get_academic_years()
        action = self.env.ref(
            "education.action_education_academic_year_evaluation")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("academic_year_id", "=", next_year.id),
             ("center_id", "=", self.next_school_id.id),
             ("course_id", "=", self.next_course_id.id)],
            safe_eval(action.domain or "[]")
        ])
        context = safe_eval(action.context or "{}")
        context.update({
            "default_academic_year_id": next_year.id,
            "default_center_id": self.next_school_id.id,
            "default_course_id": self.next_course_id.id,
        })
        action_dict.update({
            "domain": domain,
            "context": context,
        })
        return action_dict
