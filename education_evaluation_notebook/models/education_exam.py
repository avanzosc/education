# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationExam(models.Model):
    _name = "education.exam"
    _description = "Education Exam"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    exam_type_id = fields.Many2one(
        comodel_name="education.exam.type", string="Exam Type", required=True)
    n_line_id = fields.Many2one(
        comodel_name="education.notebook.line", string="Notebook Line",
        required=True, domain="[('exists_master', '=', False)]")
    schedule_id = fields.Many2one(
        comodel_name="education.schedule", related="n_line_id.schedule_id",
        string="Class Schedule", store=True)
    eval_type = fields.Selection(
        related="n_line_id.eval_type", string="Evaluation Season")
    teacher_id = fields.Many2one(
        comodel_name="hr.employee", related="n_line_id.schedule_id.teacher_id",
        string="Teacher", store=True)
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        related="n_line_id.schedule_id.academic_year_id",
        string="Academic Year", store=True)
    subject_id = fields.Many2one(
        comodel_name="education.subject",
        related="n_line_id.schedule_id.subject_id",
        string="Education Subject", store=True)
    date = fields.Date(string="Exam date")
    eval_percent = fields.Float(string="Percent (%)", required=True)
    state = fields.Selection(
        selection=[("draft", "New"),
                   ("progress", "Marking"),
                   ("done", "Graded"),
                   ("closed", "Closed"), ],
        default="draft", track_visibility="onchange")
    second_chance_exam_id = fields.Many2one(
        comodel_name="education.exam", string="Second-chance Exam Of")
    second_chance_exam_ids = fields.One2many(
        comodel_name="education.exam", inverse_name="second_chance_exam_id",
        string="Second-chance Exams")
    type_exam_name = fields.Selection(
        related="exam_type_id.e_type", string="General Exam Type")
    mark_close_date = fields.Date(string="Closing Date")
    record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="exam_id",
        string="Academic Records")
    record_count = fields.Integer(
        compute="_compute_record_count", string="# Records", store=True)
    description = fields.Text(string="Description")

    @api.multi
    def action_generate_record(self):
        record_obj = self.env["education.record"]
        for exam in self.filtered(lambda e: e.state in ('draft', 'progress')):
            n_line = exam.n_line_id
            for student in n_line.schedule_id.student_ids:
                parent_record = n_line.find_or_create_student_record(student)
                record = record_obj.search([
                    ("exam_id", "=", exam.id),
                    ("n_line_id", "=", n_line.id),
                    ("student_id", "=", student.id),
                    ("parent_record_id", "=", parent_record.id),
                ])
                if not record:
                    record_obj.create({
                        "exam_id": exam.id,
                        "student_id": student.id,
                        "n_line_id": n_line.id,
                        "parent_record_id": parent_record.id,
                        "date": exam.date,
                    })

    @api.multi
    @api.depends("record_ids")
    def _compute_record_count(self):
        for exam in self:
            exam.record_count = len(exam.record_ids)

    @api.multi
    def button_show_records(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update({
            "default_exam_id": self.id,
            "hide_calculated": True,
            "hide_behaviour": True,
            "hide_exam": False,
        })
        domain = expression.AND([
            [("exam_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def action_marking(self):
        for exam in self.filtered(lambda e: e.state == "draft"):
            if not exam.date:
                raise ValidationError(
                    _('You must set an exam date.'))
            exam.state = "progress"

    @api.multi
    def action_graded(self):
        for exam in self.filtered(lambda e: e.state == "progress"):
            exam.state = "done"

    @api.multi
    def action_close_exam(self):
        today = fields.Date.context_today(self)
        for exam in self.filtered(lambda e: e.state == "done"):
            exam.write({
                "state": "closed",
                "mark_close_date": today
            })

    @api.multi
    def action_draft(self):
        for exam in self.filtered(lambda e: e.state != "closed"):
            exam.state = "draft"
