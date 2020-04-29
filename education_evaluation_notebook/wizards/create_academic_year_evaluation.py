# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class CreateAcademicYearEvaluation(models.TransientModel):
    _name = "create.academic_year.evaluation"
    _description = "Wizard to create evaluations"

    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year", string="Academic Year")
    line_ids = fields.One2many(
        comodel_name="create.academic_year.evaluation.line",
        inverse_name="wizard_id",
        string="Education Center and Course relation")
    evaluation_number = fields.Selection(
        selection=[(1, "One"),
                   (2, "Two"),
                   (3, "Three")],
        string="Evaluation Number", default=3, required=True)
    final_evaluation = fields.Boolean(
        string="Final Evaluation", default=True)
    show_lines = fields.Boolean(default=True)

    @api.model
    def default_get(self, fields_list):
        res = super(CreateAcademicYearEvaluation, self).default_get(
            fields_list)
        if self.env.context.get("active_model") == "education.course.change":
            course_changes = self.env["education.course.change"].browse(
                self.env.context.get("active_ids"))
            res.update({
                "line_ids": [
                    (0, 0, {"center_id": c.school_id.id,
                            "course_id": c.course_id.id},
                     ) for c in course_changes],
                "show_lines": False,
            })
        if self.env.context.get("active_model") == "res.partner":
            partners = self.env["res.partner"].browse(
                self.env.context.get("active_ids"))
            line_ids = []
            for partner in partners.filtered(
                    lambda p: p.educational_category == "school"):
                courses = (partner.mapped("next_course_ids.course_id") |
                           partner.mapped("prev_course_ids.next_course_id"))
                line_ids += [(0, 0, {
                    "center_id": partner.id,
                    "course_id": course.id,
                }) for course in courses]
            res.update({
                "line_ids": line_ids,
            })
        if self.env.context.get("active_model") == "education.course":
            line_ids = []
            for course_id in self.env.context.get("active_ids"):
                course_change_obj = self.env["education.course.change"]
                centers = (
                    course_change_obj.search([
                        ('course_id', '=', course_id)]).mapped("school_id") |
                    course_change_obj.search([
                        ('next_course_id', '=', course_id)]).mapped(
                        "next_school_id"))
                line_ids += [(0, 0, {
                    "center_id": center.id,
                    "course_id": course_id,
                }) for center in centers]
            res.update({
                "line_ids": line_ids,
            })
        return res

    @api.multi
    def button_create_evaluation(self):
        self.ensure_one()
        academic_year_obj = self.env["education.academic_year"]
        academic_year = (
            self.academic_year_id or
            academic_year_obj.search([("current", "=", True)], limit=1))
        if (academic_year and (not academic_year.date_start or
                               not academic_year.date_end)):
            msg = _("Academic year must have defined start and end dates.")
            action = self.env.ref("education.action_education_academic_year")
            action_msg = _("Configure Academic Year")
            raise RedirectWarning(msg, action.id, action_msg)
        for line in self.line_ids:
            academic_year.create_evaluations(
                line.center_id, line.course_id,
                self.evaluation_number, self.final_evaluation)
        action = self.env.ref(
            "education.action_education_academic_year_evaluation")
        action_dict = action and action.read()[0] or {}
        domain = expression.AND([
            [("academic_year_id", "=", academic_year.id),
             ("center_id", "in", self.mapped("line_ids.center_id").ids),
             ("course_id", "in", self.mapped("line_ids.course_id").ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict


class CreateAcademicYearEvaluationLine(models.TransientModel):
    _name = "create.academic_year.evaluation.line"
    _description = "Wizard lines to create evaluations"

    wizard_id = fields.Many2one(
        comodel_name="create.academic_year.evaluation", string="Wizard",
        required=True)
    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center", required=True)
    course_id = fields.Many2one(
        comodel_name="education.course", string="Course", required=True)
