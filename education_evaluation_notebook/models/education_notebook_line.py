# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval
from .education_academic_year_evaluation import EVAL_TYPE


class EducationNotebookLine(models.Model):
    _name = "education.notebook.line"
    _description = "Education Notebook Line"
    _rec_name = "description"
    _order = "schedule_id,eval_type,sequence"

    def default_eval_type(self):
        default_dict = self.env[
            "education.academic_year.evaluation"].default_get(["eval_type"])
        return default_dict.get("eval_type")

    code = fields.Char(
        string="Code", help="This code is used for academic record report")
    sequence = fields.Integer(string="Sequence", default=1)
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
        selection=EVAL_TYPE, string="Evaluation Season",
        default=default_eval_type, required=True)
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
    notes = fields.Html(string="Notes")

    @api.constrains("code")
    def _check_code_length(self):
        for competence in self.filtered("code"):
            if len(competence.code) > 3:
                raise ValidationError(
                    _("Code must have a length of 3 characters "))

    @api.multi
    def button_open_notebook_line_form(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_notebook_line_action")
        form_view = self.env.ref(
            "education_evaluation_notebook.education_notebook_line_view_form")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({
            "domain": domain,
            "view_id": form_view.id,
            "view_mode": "form",
            "res_id": self.id,
            "views": [],
        })
        return action_dict

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
            "hide_calculated": self.competence_id.eval_mode == "behaviour",
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
            line.record_count = len(
                line.record_ids.filtered(lambda r: not r.exam_id))

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

    @api.onchange("parent_line_id")
    def _onchange_parent_line_id(self):
        for line in self:
            line.eval_type = line.parent_line_id.eval_type

    @api.multi
    def find_or_create_student_record(self, student, parent_record=False):
        self.ensure_one()
        record_obj = self.env["education.record"]
        if self.parent_line_id:
            parent_record = (
                self.parent_line_id.find_or_create_student_record(student))
        record_domain = [
            ("n_line_id", "=", self.id),
            ("student_id", "=", student.id),
            ("exam_id", "=", False),
        ]
        if parent_record:
            record_domain = expression.AND(
                [record_domain, [("parent_record_id", "=", parent_record.id)]])
        record = record_obj.search(record_domain)
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
            field = record._fields["eval_type"]
            eval_type = field.convert_to_export(record["eval_type"], record)
            result.append(
                (record.id,
                 "{} [{}]".format(record.description, eval_type)))
        return result
