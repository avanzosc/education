# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationSchedule(models.Model):
    _inherit = "education.schedule"

    notebook_line_ids = fields.One2many(
        comodel_name="education.notebook.line",
        inverse_name="schedule_id",
        string="Notebook Lines",
    )
    notebook_line_count = fields.Integer(
        compute="_compute_notebook_line_count",
        string="# Notebook Lines",
        store=True,
    )
    master_notebook_line_ids = fields.One2many(
        comodel_name="education.notebook.line",
        inverse_name="schedule_id",
        string="Master Notebook Lines",
        domain=['|', ('evaluation_competence', '=', True),
                ('global_competence', '=', True)],
    )
    exam_ids = fields.One2many(
        comodel_name="education.exam",
        inverse_name="schedule_id",
        string="Exams",
    )
    exam_count = fields.Integer(
        compute="_compute_exam_count",
        string="# Exams",
        store=True,
    )
    record_ids = fields.One2many(
        comodel_name="education.record",
        inverse_name="schedule_id",
        string="Academic Records",
    )
    record_count = fields.Integer(
        compute="_compute_record_count",
        string="# Records",
        store=True,
    )
    homework_ids = fields.One2many(
        comodel_name="education.homework",
        inverse_name="schedule_id",
        string="Homework",
    )
    homework_count = fields.Integer(
        compute="_compute_homework_count",
        string="# Homework",
        store=True,
    )

    @api.multi
    @api.depends("homework_ids")
    def _compute_homework_count(self):
        for schedule in self:
            schedule.homework_count = len(schedule.homework_ids)

    @api.multi
    @api.depends("notebook_line_ids")
    def _compute_notebook_line_count(self):
        for schedule in self:
            schedule.notebook_line_count = len(schedule.notebook_line_ids)

    @api.multi
    @api.depends("exam_ids")
    def _compute_exam_count(self):
        for schedule in self:
            schedule.exam_count = len(schedule.exam_ids)

    @api.multi
    @api.depends("record_ids")
    def _compute_record_count(self):
        for schedule in self:
            schedule.record_count = len(schedule.record_ids)

    @api.multi
    def button_show_homework(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_homework_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update(
            {"default_schedule_id": self.id})
        domain = expression.AND([
            [("schedule_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def button_show_records(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        action_dict["views"] = action_dict.get("views", [])
        action_dict["views"].append((False, "pivot"))
        domain = expression.AND([
            [("n_line_id", "in", self.notebook_line_ids.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def button_show_exams(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_exam_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update(
            {"default_schedule_id": self.id})
        domain = expression.AND([
            [("schedule_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def button_show_notebook_lines(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_notebook_line_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update(
            {"default_schedule_id": self.id})
        domain = expression.AND([
            [("schedule_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def get_notebook_line_vals(
            self, competence, parent_line=False, percent=False,
            evaluation=False):
        self.ensure_one()
        sequence = 10
        if competence.global_check:
            sequence = 0
        elif competence.evaluation_check:
            if evaluation.eval_type == "first":
                sequence = 1
            elif evaluation.eval_type == "second":
                sequence = 2
            elif evaluation.eval_type == "third":
                sequence = 3
            else:
                sequence = 4
        vals = {
            "schedule_id": self.id,
            "competence_id": competence.id,
            "description": (self.subject_id.description or
                            self.task_type_id.description),
            "eval_percent": percent or 100.0,
            "eval_type": evaluation and evaluation.eval_type or "final",
            "parent_line_id": parent_line and parent_line.id,
            "sequence": sequence,
        }
        return vals

    @api.multi
    def find_or_create_notebook_line(
            self, competence, parent_line=False, percent=False,
            evaluation=False):
        self.ensure_one()
        notebook_line_obj = self.env["education.notebook.line"]
        record = notebook_line_obj.sudo().search([
            ("schedule_id", "=", self.id),
            ("competence_id", "=", competence.id),
            ("eval_type", "=", evaluation and evaluation.eval_type or "final"),
        ])
        if not record:
            notebook_vals = self.get_notebook_line_vals(
                competence, parent_line=parent_line, percent=percent,
                evaluation=evaluation)
            record = notebook_line_obj.create(notebook_vals)
        return record

    @api.multi
    def generate_global_notebook_lines(self):
        global_competences = self.env["education.competence"].search([
            ("global_check", "=", True)])
        for schedule in self:
            for global_competence in global_competences:
                schedule.find_or_create_notebook_line(global_competence)
        return True

    @api.multi
    def generate_evaluation_notebook_lines(self):
        evaluation_obj = self.env["education.academic_year.evaluation"]
        template_obj = self.env["education.notebook.template"]
        evaluation_competences = self.env["education.competence"].search([
            ("evaluation_check", "=", True)])
        for schedule in self:
            courses = schedule.mapped("group_ids.course_id")
            global_lines = schedule.notebook_line_ids.filtered(
                lambda l: l.competence_id.global_check)
            evaluations = evaluation_obj.search([
                ("academic_year_id", "=", schedule.academic_year_id.id),
                ("center_id", "=", schedule.center_id.id),
            ])
            if courses:
                evaluations = evaluations.filtered(
                    lambda e: e.course_id in courses)
            else:
                evaluations = evaluations.filtered(
                    lambda e: not e.course_id)
            eval_number = list(dict.fromkeys(evaluations.mapped('eval_type')))
            percent = 100 / (len(eval_number) or 1.0)
            for eval_competence in evaluation_competences:
                for global_line in global_lines:
                    for evaluation in evaluations:
                        evaluation_line = (
                            schedule.find_or_create_notebook_line(
                                eval_competence, global_line, percent,
                                evaluation))
                        for course in courses:
                            templates = template_obj.find_template_line(
                                schedule.center_id, schedule.task_type_id,
                                course=course, subject=schedule.subject_id,
                                eval_type=evaluation.eval_type)
                            templates.create_notebook_line(
                                schedule=schedule,
                                parent_line=evaluation_line)
        return True

    @api.multi
    def action_generate_notebook_lines(self):
        for schedule in self:
            schedule.generate_global_notebook_lines()
            schedule.generate_evaluation_notebook_lines()

    @api.multi
    def action_generate_records(self):
        self.mapped('notebook_line_ids').button_create_student_records()

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
            name_tuple = super(EducationSchedule, record).name_get()
            name = name_tuple[0][1] if name_tuple and name_tuple[0] else ""
            if self.env.context.get("show_groups"):
                name = "{} [{}]".format(name, ", ".join(
                    record.mapped("group_ids.display_name")))
            result.append((record.id, name))
        return result
