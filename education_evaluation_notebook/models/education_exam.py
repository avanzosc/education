# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationExam(models.Model):
    _name = "education.exam"
    _description = "Education Exam"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    exam_type_id = fields.Many2one(
        comodel_name="education.exam.type", string="Exam Type", required=True)
    exam_etype = fields.Selection(
        string="Type", related="exam_type_id.e_type")
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
    date = fields.Date(string="Exam date", copy=False)
    eval_percent = fields.Float(string="Percent (%)", required=True)
    state = fields.Selection(
        selection=[("draft", "New"),
                   ("progress", "Marking"),
                   ("done", "Graded"),
                   ("closed", "Closed"), ],
        default="draft", track_visibility="onchange", string="State",
        copy=False)
    recovered_exam_id = fields.Many2one(
        comodel_name="education.exam", string="Recovered Exam")
    recovered_exam_type_id = fields.Many2one(
        comodel_name="education.exam.type", string="Recovered Exam Type",
        related="recovered_exam_id.exam_type_id")
    retake_ids = fields.One2many(
        comodel_name="education.exam", inverse_name="recovered_exam_id",
        string="Retake Exams")
    retake_count = fields.Integer(
        compute="_compute_retake_count", string="# Retakes")
    mark_close_date = fields.Date(string="Closing Date", copy=False)
    record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="exam_id",
        string="Academic Records")
    record_count = fields.Integer(
        compute="_compute_record_count", string="# Records", store=True)
    description = fields.Text(string="Description")

    @api.multi
    def find_or_create_student_record(self, student, parent_record):
        self.ensure_one()
        record_obj = self.env["education.record"]
        exam_record = (
            self.recovered_exam_id.find_or_create_student_record(
                student, parent_record) if self.recovered_exam_id else False)
        if not exam_record or (exam_record and
                               exam_record.pass_mark == "fail"):
            record = record_obj.search([
                ("exam_id", "=", self.id),
                ("n_line_id", "=", self.n_line_id.id),
                ("student_id", "=", student.id),
                ("parent_record_id", "=", parent_record.id),
            ])
            if not record:
                record_vals = {
                    "exam_id": self.id,
                    "student_id": student.id,
                    "n_line_id": self.n_line_id.id,
                    "parent_record_id": parent_record.id,
                    "date": self.date,
                    "recovered_record_id": exam_record and exam_record.id,
                }
                record_obj.create(record_vals)
            return record

    @api.multi
    def action_generate_record(self):
        for exam in self.filtered(lambda e: e.state in ('draft', 'progress')):
            n_line = exam.n_line_id
            for student in n_line.schedule_id.student_ids:
                parent_record = n_line.find_or_create_student_record(student)
                self.find_or_create_student_record(student, parent_record)

    @api.multi
    @api.depends("record_ids")
    def _compute_record_count(self):
        for exam in self:
            exam.record_count = len(exam.record_ids)

    @api.multi
    @api.depends("retake_ids")
    def _compute_retake_count(self):
        for exam in self:
            exam.retake_count = len(exam.retake_ids)

    @api.multi
    @api.onchange("recovered_exam_id")
    def _onchange_recovered_exam(self):
        for exam in self.filtered("recovered_exam_id"):
            exam.n_line_id = exam.recovered_exam_id.n_line_id
            exam.eval_percent = exam.recovered_exam_id.eval_percent

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
    def button_show_retakes(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_exam_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update({
            "default_recovered_exam_id": self.id,
        })
        domain = expression.AND([
            [("recovered_exam_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def action_marking(self):
        for exam in self.filtered(lambda e: e.state in ["draft", "done"]):
            if exam.state == "draft":
                if not exam.date:
                    raise ValidationError(
                        _('You must set an exam date.'))
                exam.action_generate_record()
            exam.state = "progress"

    @api.multi
    def action_graded(self):
        for exam in self.filtered(lambda e: e.state == "progress"):
            exam.state = "done"
            exam.record_ids.write({
                "state": "assessed",
            })

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

    @api.multi
    def retake_exam(self):
        self.ensure_one()
        exam = self.copy(default={
            "recovered_exam_id": self.id,
            "exam_type_id": (
                self.exam_type_id.retake_type_id.id
                if self.exam_type_id.retake_type_id else self.exam_type_id.id),
        })
        action = self.env.ref(
            "education_evaluation_notebook.education_exam_action")
        action_dict = action.read()[0] if action else {}
        action_dict.update({
            "res_id": exam.id,
            "views": [(self.env.ref("education_evaluation_notebook."
                                    "education_exam_view_form").id, 'form')]
        })
        return action_dict

    @api.multi
    def unlink(self):
        for exam in self:
            if exam.state != "draft":
                raise UserError(
                    _("You can only delete an exam in draft state."))
        return super(EducationExam, self).unlink()

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
            name = record.name
            if (record.exam_type_id.e_type == "secondchance" or
                    record.recovered_exam_id):
                name = _("[RETAKE] {}").format(name)
            result.append((record.id, name))
        return result
