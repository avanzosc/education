# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from .education_academic_year_evaluation import EVAL_TYPE


class EducationNotebookTemplate(models.Model):
    _name = "education.notebook.template"
    _description = "Evaluation Notebook Template"

    def default_eval_type(self):
        default_dict = self.env[
            "education.academic_year.evaluation"].default_get(["eval_type"])
        return default_dict.get("eval_type")

    education_center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain="[('educational_category', '=', 'school')]", required=True)
    parent_center_id = fields.Many2one(
        comodel_name="res.partner", string="Related Company",
        related="education_center_id.parent_id", store=True)
    course_id = fields.Many2one(
        comodel_name="education.course", string="Course")
    subject_id = fields.Many2one(
        comodel_name="education.subject", string="Education Subject")
    task_type_id = fields.Many2one(
        comodel_name="education.task_type", string="Task Type", required=True)
    eval_type = fields.Selection(
        selection=EVAL_TYPE, string="Evaluation Season",
        default=default_eval_type, required=True)
    competence_id = fields.Many2one(
        comodel_name="education.competence", string="Competence",
        domain="[('evaluation_check', '!=', True), "
               "('global_check', '!=', True)]", required=True)
    competence_type_id = fields.Many2one(
        comodel_name="education.competence.type", string="Competence Type")
    name = fields.Char(string="Description", required=True)
    eval_percent = fields.Float(
        string="Percent (%)", default=100.0, group_operator="max")

    def find_template_line(
            self, center, task_type, course=False, subject=False,
            eval_type=False):
        return self.search([
            ("education_center_id", "=", center.id),
            ("task_type_id", "=", task_type.id),
            "|", ("course_id", "=", course.id), ("course_id", "=", False),
            "|", ("subject_id", "=", subject.id), ("subject_id", "=", False),
            ("eval_type", "=", eval_type)
        ])

    @api.multi
    def get_notebook_line_vals(self, schedule, parent_line=False):
        self.ensure_one()
        vals = {
            "schedule_id": schedule.id,
            "competence_id": self.competence_id.id,
            "description": self.name,
            "eval_percent": self.eval_percent,
            "evaluation_id":
                parent_line and parent_line.evaluation_id and
                parent_line.evaluation_id.id or False,
            "eval_type": self.eval_type,
            "competence_type_id": self.competence_type_id.id,
            "parent_line_id": parent_line and parent_line.id or False,
        }
        return vals

    @api.multi
    def create_notebook_line(self, schedule=False, parent_line=False):
        notebook_obj = self.env["education.notebook.line"]
        for template in self:
            notebook_vals = template.get_notebook_line_vals(
                schedule, parent_line=parent_line)
            notebook_line = notebook_obj.search([
                ("description", "=", notebook_vals.get("description")),
                ("parent_line_id", "=", notebook_vals.get("parent_line_id")),
                ("schedule_id", "=", notebook_vals.get("schedule_id")),
                ("evaluation_id", "=", notebook_vals.get("evaluation_id")),
                ("competence_id", "=", notebook_vals.get("competence_id")),
            ])
            if not notebook_line:
                notebook_obj.create(notebook_vals)
