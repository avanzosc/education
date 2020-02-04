# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationNotebookLine(models.Model):
    _name = "education.notebook.line"
    _description = "Education Notebook Line"
    _rec_name = "description"

    @api.model
    def _get_selection_eval_type(self):
        return self.env["education.academic_year.evaluation"].fields_get(
            allfields=["eval_type"])["eval_type"]["selection"]

    def default_eval_type(self):
        default_dict = self.env[
            "education.academic_year.evaluation"].default_get(["eval_type"])
        return default_dict.get("eval_type")

    schedule_id = fields.Many2one(
        comodel_name="education.schedule", string="Class Schedule",
        required=True)
    teacher_id = fields.Many2one(
        related="schedule_id.teacher_id", comodel_name="hr.employee",
        string="Teacher", store=True)
    a_year_id = fields.Many2one(
        related="schedule_id.academic_year_id",
        comodel_name="education.academic_year",
        string="Academic Year", store=True)
    education_center_id = fields.Many2one(
        related="schedule_id.center_id", comodel_name="res.partner",
        string="Education Center", store=True)
    classroom_id = fields.Many2one(
        related="schedule_id.classroom_id", comodel_name="education.classroom",
        string="Classroom", store=True)
    task_type_id = fields.Many2one(
        related="schedule_id.task_type_id", comodel_name="education.task_type",
        string="Task Type", store=True)
    subject_id = fields.Many2one(
        related="schedule_id.subject_id", comodel_name="education.subject",
        string="Education Subject", store=True)
    competence_id = fields.Many2one(
        comodel_name="education.competence", string="Competence",
        required=True)
    description = fields.Char(string="Description", required=True)
    eval_percent = fields.Float(string="Percent (%)", default=100.0)
    eval_type = fields.Selection(
        selection="_get_selection_eval_type", string="Evaluation Season",
        default=default_eval_type, required=True)
    evaluation_id = fields.Many2one(
        comodel_name="education.academic_year.evaluation", string="Evaluation")
    exam_ids = fields.One2many(
        comodel_name="education.exam", inverse_name="n_line_id",
        tring="Exams", editable=True)
    exam_count = fields.Integer(
        compute="_compute_exam_count", string="# Exams")
    competence_type_id = fields.Many2one(
        comodel_name="education.competence.type", string="Competence Type")
    parent_line_id = fields.Many2one(
        comodel_name="education.notebook.line", string="Parent Line")
    child_line_ids = fields.One2many(
        comodel_name="education.notebook.line", inverse_name="parent_line_id",
        string="Child Lines")
    child_line_count = fields.Integer(
        compute="_compute_child_line_count", string="# Child Lines")
    parent_parent_line_id = fields.Many2one(
        comodel_name="education.notebook.line", string="Parent Parent Line",
        related="parent_line_id.parent_line_id", store=True)
    exists_master = fields.Boolean(
        string="Is master", compute="_compute_master_competences", store=True)
    evaluation_competence = fields.Boolean(
        related="competence_id.evaluation_check", store=True,
        string="Evaluation Competence")
    global_competence = fields.Boolean(
        related="competence_id.global_check", store=True,
        string="Global Competence")
    record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="n_line_id",
        string="Academic Records")
    record_count = fields.Integer(
        compute="_compute_record_count", string="# Academic Record",
        store=True)

    @api.multi
    def button_show_child_lines(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_notebook_line_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("parent_line_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def button_show_records(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update({
            "hide_numeric": self.competence_id.eval_mode == "behaviour",
            "hide_behaviour": self.competence_id.eval_mode == "numeric",
        })
        domain = expression.AND([
            [("n_line_id", "=", self.id),
             ("exam_id", "=", False)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    @api.depends("record_ids")
    def _compute_record_count(self):
        for line in self:
            line.record_count = len(line.record_ids)

    @api.multi
    @api.depends("competence_id", "competence_id.evaluation_check",
                 "competence_id.global_check")
    def _compute_master_competences(self):
        for line in self:
            line.exists_master = (
                line.competence_id.evaluation_check or
                line.competence_id.global_check or False)

    @api.multi
    @api.depends("exam_ids")
    def _compute_exam_count(self):
        for record in self:
            record.exam_count = len(record.exam_ids)

    @api.onchange("competence_id")
    def _onchange_competence_id(self):
        for line in self:
            line.description = line.competence_id.name or ""

    @api.onchange("evaluation_id")
    def _onchange_evaluation_id(self):
        for line in self:
            line.eval_type = line.evaluation_id.eval_type or "final"

    @api.onchange("parent_line_id")
    def _onchange_parent_line_id(self):
        for line in self:
            line.evaluation_id = line.parent_line_id.evaluation_id
            line._onchange_evaluation_id()

    @api.multi
    def find_or_create_student_record(self, student, parent_record=False):
        self.ensure_one()
        record_obj = self.env["education.record"]
        if self.parent_line_id:
            parent_record = (
                self.parent_line_id.find_or_create_student_record(student))
        record = record_obj.search([
            ("n_line_id", "=", self.id),
            ("student_id", "=", student.id),
            ("exam_id", "=", False),
        ])
        if not record:
            record = record_obj.create({
                "n_line_id": self.id,
                "student_id": student.id,
                "parent_record_id": parent_record and parent_record.id,
            })
        return record

    @api.multi
    def button_create_student_records(self):
        for line in self:
            for student in line.schedule_id.student_ids:
                line.find_or_create_student_record(student)
            line.exam_ids.action_generate_record()

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            result.append(
                (record.id,
                 "{} [{}]".format(record.description, record.eval_type)))
        return result
