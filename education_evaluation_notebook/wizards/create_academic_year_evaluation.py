# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


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
                   (3, "Three"),
                   (4, "Four")],
        string="Evaluation Number", default=1, required=True)

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
        for course_change in self.course_change_ids:
            course_change.create_evaluations(
                evaluation_number=self.evaluation_number,
                academic_year=self.academic_year_id)
