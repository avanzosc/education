# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval
from .education_academic_year_evaluation import EVAL_TYPE

RECORD_STATE = [
    ("initial", "Initial"),
    ("assessed", "Assessed"),
]

RECORD_EXCEPTIONALITY = [
    ("exempt", "Exempt"),
    ("not_taken", "Not Taken"),
    ("not_evaluated", "Not Evaluated"),
    ("adaptation", "ICA"),
    ("reinforcement", "IERP")
]


class EducationRecord(models.Model):
    _name = "education.record"
    _description = "Academic Record"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]

    @api.model
    def _get_selection_exam_state(self):
        return self.env["education.exam"].fields_get(
            allfields=["state"])["state"]["selection"]

    exam_id = fields.Many2one(
        comodel_name="education.exam", string="Exam", ondelete="cascade")
    exam_type_id = fields.Many2one(
        comodel_name="education.exam.type", related="exam_id.exam_type_id",
        string="Exam Type", store=True)
    exam_eval_percent = fields.Float(
        compute="_compute_eval_percent", string="Percent (%)")
    exam_state = fields.Selection(
        selection="_get_selection_exam_state", string="Exam State",
        related="exam_id.state", store=True)
    date = fields.Date(
        related="exam_id.date", string="Exam Date", store=True)
    n_line_id = fields.Many2one(
        comodel_name="education.notebook.line", string="Notebook Line",
        required=True, ondelete="cascade")
    competence_id = fields.Many2one(
        related="n_line_id.competence_id", comodel_name="education.competence",
        store=True, string="Competence")
    competence_eval_mode = fields.Selection(
        related="n_line_id.competence_id.eval_mode", string="Evaluation Mode",
        store=True)
    evaluation_competence = fields.Boolean(
        related="n_line_id.competence_id.evaluation_check",
        string="Evaluation Competence", store=True)
    global_competence = fields.Boolean(
        related="n_line_id.competence_id.global_check",
        string="Global Competence", store=True)
    schedule_id = fields.Many2one(
        comodel_name="education.schedule", related="n_line_id.schedule_id",
        string="Class Schedule", store=True)
    subject_id = fields.Many2one(
        comodel_name="education.subject", string="Education Subject",
        related="n_line_id.schedule_id.subject_id", store=True)
    subject_name = fields.Char(
        string="Subject Name", compute="_compute_subject_name")
    teacher_id = fields.Many2one(
        comodel_name="hr.employee", related="n_line_id.schedule_id.teacher_id",
        string="Teacher", store=True)
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        related="n_line_id.schedule_id.academic_year_id",
        string="Academic Year", store=True)
    evaluation_id = fields.Many2one(
        comodel_name="education.academic_year.evaluation",
        compute="_compute_evaluation_id", string="Evaluation", store=True)
    eval_type = fields.Selection(
        selection=EVAL_TYPE, related="n_line_id.eval_type",
        string="Evaluation Season", store=True)
    student_id = fields.Many2one(
        comodel_name="res.partner", string="Student", required=True,
        ondelete="cascade")
    numeric_mark = fields.Float(string="Official Mark")
    behaviour_mark_id = fields.Many2one(
        comodel_name="education.mark.behaviour", string="Behaviour Mark")
    calculated_numeric_mark = fields.Float(
        compute="_compute_generate_marks", string="Calculated Numeric Mark",
        store=True)
    calculated_partial_mark = fields.Float(
        compute="_compute_partial_marks", string="Calculated Partial Mark",
        store=True)
    mark_id = fields.Many2one(
        comodel_name="education.mark.numeric", string="Numeric Mark (Text)",
        compute="_compute_mark_id", store=True)
    n_mark_reduced_name = fields.Char(
        related="mark_id.reduced_name", comodel_name="education.mark.numeric",
        string="Reduced Numeric Mark", store=True)
    parent_record_id = fields.Many2one(
        comodel_name="education.record", string="Parent Record")
    child_record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="parent_record_id",
        string="Academic Records", editable=True)
    child_record_count = fields.Integer(
        compute="_compute_child_record_count",
        string="# Child Records", store=True)
    state = fields.Selection(
        selection=RECORD_STATE, string="Record State", default="initial")
    exceptionality = fields.Selection(
        selection=RECORD_EXCEPTIONALITY, string="Exceptionality",
        help="* Exempt: When the student does not have any record or exam.\n"
             "* Not Taken: When the student did not take the .\n"
             "* Not Evaluated: When the student was not able to take .\n"
             "* ICA: Individual Curriculum Adaptation.\n"
             "* IERP: Individual Educational Reinforcement Plan.")
    line_parent_id = fields.Many2one(
        comodel_name="education.notebook.line",
        related="n_line_id.parent_line_id",
        string="Parent Notebook Line", store=True)
    line_parent_parent_id = fields.Many2one(
        comodel_name="education.notebook.line",
        related="n_line_id.parent_parent_line_id",
        string="Parent Parent Notebook Line", store=True)

    @api.multi
    @api.depends("student_id", "eval_type", "n_line_id",
                 "n_line_id.schedule_id", "n_line_id.schedule_id.group_ids",
                 "n_line_id.schedule_id.group_ids.student_ids",
                 "n_line_id.schedule_id.group_ids.course_id",
                 "n_line_id.schedule_id.group_ids.center_id",
                 "n_line_id.schedule_id.academic_year_id")
    def _compute_evaluation_id(self):
        for record in self:
            schedule = record.n_line_id.schedule_id
            group = schedule.group_ids.filtered(
                lambda g: record.student_id in g.student_ids)
            evaluations = schedule.academic_year_id.evaluation_ids
            record.evaluation_id = evaluations.filtered(
                lambda e: e.center_id == group.center_id and
                e.course_id == group.course_id and
                e.eval_type == record.eval_type)

    @api.multi
    @api.depends("child_record_ids")
    def _compute_child_record_count(self):
        for record in self:
            record.child_record_count = len(record.child_record_ids)

    @api.multi
    @api.depends("numeric_mark", "n_line_id", "n_line_id.competence_id",
                 "n_line_id.competence_id.eval_mode", "exceptionality")
    def _compute_mark_id(self):
        mark_obj = self.env["education.mark.numeric"]
        for record in self:
            if (record.exceptionality != "exempt" and
                    record.competence_eval_mode != "behaviour"):
                record.mark_id = mark_obj.search([
                    ("initial_mark", "<=", record.numeric_mark),
                    ("final_mark", ">=", record.numeric_mark)], limit=1)

    @api.multi
    @api.depends("student_id", "academic_year_id", "subject_id")
    def _compute_subject_name(self):
        for record in self:
            student_group = record.student_id.get_current_group(
                academic_year=record.academic_year_id)
            record.subject_name = self.subject_id.get_subject_name(
                student_group.center_id, student_group.level_id,
                student_group.course_id, record.schedule_id.language_id)

    @api.multi
    def button_set_draft(self):
        self.filtered(lambda r: r.state == "assessed").write({
            "state": "initial",
        })

    @api.multi
    def button_set_assessed(self):
        self.filtered(lambda r: r.state == "initial").write({
            "state": "assessed",
        })

    @api.multi
    def button_set_exempt(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": "exempt",
        })

    @api.multi
    def button_set_not_taken(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": "not_taken",
        })

    @api.multi
    def button_set_not_evaluated(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": "not_evaluated",
        })

    @api.multi
    def button_set_adaptation(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": "adaptation",
        })

    @api.multi
    def button_set_reinforcement(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": "reinforcement",
        })

    @api.multi
    def button_remove_exceptionality(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": False,
        })

    @api.multi
    def button_show_records(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update(
            {"default_parent_record_id": self.id})
        domain = expression.AND([
            [("id", "in", self.child_record_ids.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    @api.depends("exam_id", "exam_id.eval_percent",
                 "n_line_id", "n_line_id.eval_percent")
    def _compute_eval_percent(self):
        for record in self:
            record.exam_eval_percent = (
                record.exam_id.eval_percent if record.exam_id else
                record.n_line_id.eval_percent)

    @api.multi
    @api.depends("child_record_ids", "child_record_ids.numeric_mark",
                 "child_record_ids.exam_eval_percent",
                 "child_record_ids.state")
    def _compute_generate_marks(self):
        for record in self:
            mark_records = record.child_record_ids.filtered(
                lambda r: r.state == "assessed")
            if mark_records:
                record.calculated_numeric_mark = sum(
                    [x.numeric_mark * x.exam_eval_percent / 100
                     for x in mark_records])

    @api.multi
    def is_partial_assessed(self):
        self.ensure_one()
        if self.child_record_ids:
            return any(x.is_partial_assessed() for x in self.child_record_ids)
        elif self.state == "assessed" or (
                not self.exam_id and self.numeric_mark != 0):
            return True
        return False

    @api.multi
    @api.depends("numeric_mark", "child_record_ids",
                 "child_record_ids.numeric_mark",
                 "child_record_ids.calculated_partial_mark",
                 "child_record_ids.exam_eval_percent",
                 "child_record_ids.state")
    def _compute_partial_marks(self):
        for record in self:
            mark_records = record.child_record_ids
            partial_mark = eval_percent = 0.0
            for mark_record in mark_records:
                if mark_record.is_partial_assessed():
                    eval_percent += mark_record.exam_eval_percent
                    partial_mark += (
                        (mark_record.numeric_mark or
                         mark_record.calculated_partial_mark) *
                        mark_record.exam_eval_percent)
            record.calculated_partial_mark = (
                record.numeric_mark if not eval_percent else
                (partial_mark / eval_percent))

    @api.constrains("competence_id", "numeric_mark")
    def _check_numeric_mark_range(self):
        for record in self:
            min_mark = record.competence_id.min_mark
            max_mark = record.competence_id.max_mark
            if not (min_mark <= record.numeric_mark <= max_mark):
                raise ValidationError(
                    _("Numeric mark must be between {} and {}").format(
                        min_mark, max_mark))

    @api.multi
    def action_copy_calculated_mark(self):
        for record in self.filtered(lambda r: r.state == "initial"):
            record.write({
                "numeric_mark": record.calculated_numeric_mark,
            })

    @api.multi
    def action_copy_partial_calculated_mark(self):
        for record in self.filtered(lambda r: r.state == "initial"):
            record.write({
                "numeric_mark": record.calculated_partial_mark,
            })
