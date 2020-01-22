# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class CreateAcademicYearEvaluation(models.TransientModel):
    _name = "create.academic_year.evaluation"
    _description = "Wizard to create evaluations from course change"

    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year")
    course_change_ids = fields.Many2many(
        comodel_name="education.course.change")
    evaluation_number = fields.Selection(
        selection=[(1, "One"),
                   (2, "Two"),
                   (3, "Three")],
        string="Evaluation Number", default=1, required=True)
    final_evaluation = fields.Boolean(
        string="Final Evaluation")

    @api.model
    def default_get(self, fields_list):
        res = super(CreateAcademicYearEvaluation, self).default_get(
            fields_list)
        if self.env.context.get("active_model") == "education.course.change":
            res.update({
                "course_change_ids": [
                    (6, 0, self.env.context.get("active_ids"))],
            })
        return res

    @api.multi
    def button_create_evaluation(self):
        self.ensure_one()
        if (self.academic_year_id and (not self.academic_year_id.date_start or
                                       not self.academic_year_id.date_end)):
            msg = _("Academic year must have defined start and end dates.")
            action = self.env.ref("education.action_education_academic_year")
            action_msg = _("Configure Academic Year")
            raise RedirectWarning(msg, action.id, action_msg)
        for course_change in self.course_change_ids:
            course_change.create_evaluations(
                evaluation_number=self.evaluation_number,
                academic_year=self.academic_year_id,
                final_evaluation=self.final_evaluation)
        action = self.env.ref(
            "education.action_education_academic_year_evaluation")
        action_dict = action and action.read()[0] or {}
        domain = expression.AND([
            [("academic_year_id", "=", self.academic_year_id.id),
             ("center_id", "in",
              self.mapped("course_change_ids.school_id").ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
