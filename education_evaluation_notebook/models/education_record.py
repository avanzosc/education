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
    ("reinforcement", "IERP"),
    ("pending", "Pending to Pass")
]


class EducationRecord(models.Model):
    _name = "education.record"
    _description = "Academic Record"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "n_line_id,student_id"

    @api.model
    def _get_selection_exam_state(self):
        return self.env["education.exam"].fields_get(
            allfields=["state"])["state"]["selection"]

    exam_id = fields.Many2one(
        comodel_name="education.exam", string="Exam", ondelete="cascade",
        index=True)
    exam_type_id = fields.Many2one(
        comodel_name="education.exam.type", related="exam_id.exam_type_id",
        string="Exam Type", store=True)
    exam_eval_percent = fields.Float(
        compute="_compute_eval_percent", string="Percent (%)", store=True)
    exam_state = fields.Selection(
        selection="_get_selection_exam_state", string="Exam State",
        related="exam_id.state", store=True)
    date = fields.Date(
        related="exam_id.date", string="Exam Date", store=True)
    n_line_id = fields.Many2one(
        comodel_name="education.notebook.line", string="Notebook Line",
        required=True, ondelete="cascade", index=True)
    competence_id = fields.Many2one(
        related="n_line_id.competence_id", comodel_name="education.competence",
        store=True, string="Competence", index=True)
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
        string="Class Schedule", store=True, index=True)
    subject_id = fields.Many2one(
        comodel_name="education.subject", string="Education Subject",
        related="n_line_id.schedule_id.subject_id", store=True, index=True)
    subject_name = fields.Char(
        string="Subject Name", compute="_compute_subject_name", index=True)
    teacher_id = fields.Many2one(
        comodel_name="hr.employee", related="n_line_id.schedule_id.teacher_id",
        string="Teacher", store=True, index=True)
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        related="n_line_id.schedule_id.academic_year_id",
        string="Academic Year", store=True, index=True)
    evaluation_id = fields.Many2one(
        comodel_name="education.academic_year.evaluation",
        compute="_compute_evaluation_id", string="Evaluation", store=True,
        compute_sudo=True, index=True)
    eval_type = fields.Selection(
        selection=EVAL_TYPE, related="n_line_id.eval_type",
        string="Evaluation Season", store=True)
    student_id = fields.Many2one(
        comodel_name="res.partner", string="Student", required=True,
        ondelete="cascade", index=True)
    numeric_mark = fields.Float(string="Official Mark", group_operator="max")
    behaviour_mark_id = fields.Many2one(
        comodel_name="education.mark.behaviour", string="Behaviour Mark",
        copy=False)
    calculated_numeric_mark = fields.Float(
        compute="_compute_generate_marks", string="Calculated Numeric Mark",
        store=True, group_operator="max")
    calculated_partial_mark = fields.Float(
        compute="_compute_partial_marks", string="Calculated Partial Mark",
        store=True, group_operator="max")
    mark_id = fields.Many2one(
        comodel_name="education.mark.numeric", string="Numeric Mark (Text)",
        compute="_compute_mark_id", store=True, index=True)
    n_mark_reduced_name = fields.Char(
        related="mark_id.reduced_name", comodel_name="education.mark.numeric",
        string="Reduced Numeric Mark", store=True, index=True)
    parent_record_id = fields.Many2one(
        comodel_name="education.record", string="Parent Record", index=True)
    child_record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="parent_record_id",
        string="Academic Records", editable=True)
    child_record_count = fields.Integer(
        compute="_compute_child_record_count",
        string="# Child Records", store=True, compute_sudo=True)
    state = fields.Selection(
        selection=RECORD_STATE, string="Record State", default="initial")
    exceptionality = fields.Selection(
        selection=RECORD_EXCEPTIONALITY, string="Exceptionality",
        help="* Exempt: When the student does not have any record or exam.\n"
             "* Not Taken: When the student did not do the expected.\n"
             "* Not Evaluated: When the student was not able.\n"
             "* ICA: Individual Curriculum Adaptation.\n"
             "* IERP: Individual Educational Reinforcement Plan.\n"
             "* Pending to Pass: subject from previous course.", copy=False)
    line_parent_id = fields.Many2one(
        comodel_name="education.notebook.line",
        related="n_line_id.parent_line_id",
        string="Parent Notebook Line", store=True)
    line_parent_parent_id = fields.Many2one(
        comodel_name="education.notebook.line",
        related="n_line_id.parent_parent_line_id",
        string="Parent Parent Notebook Line", store=True)
    pass_mark = fields.Selection(
        selection=[('pass', 'Pass'),
                   ('fail', 'Fail')],
        string="Passed Mark", compute="_compute_pass_mark", store=True)
    recovered_record_id = fields.Many2one(
        comodel_name="education.record", string="Recovering Record",
        index=True)
    retake_record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="recovered_record_id",
        string="Retake Records")
    retake_record_count = fields.Integer(
        compute="_compute_retake_record_count",
        string="# Retake Records", store=True)
    comments = fields.Text(string="Comments")

    @api.multi
    @api.depends("numeric_mark", "n_line_id", "n_line_id.competence_id",
                 "n_line_id.competence_id.passed_mark")
    def _compute_pass_mark(self):
        for record in self:
            record.pass_mark = (
                'fail' if record.numeric_mark <
                record.n_line_id.competence_id.passed_mark else 'pass')

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
    @api.depends("retake_record_ids")
    def _compute_retake_record_count(self):
        for record in self:
            record.retake_record_count = len(record.retake_record_ids)

    @api.multi
    @api.depends("numeric_mark", "n_line_id", "n_line_id.competence_id",
                 "n_line_id.competence_id.eval_mode", "exceptionality")
    def _compute_mark_id(self):
        mark_obj = self.env["education.mark.numeric"]
        for record in self:
            if (record.exceptionality != "exempt" and
                    record.competence_eval_mode != "behaviour"):
                record.mark_id = mark_obj._get_mark(
                    round(record.numeric_mark, 2))

    @api.multi
    @api.depends("student_id", "academic_year_id", "subject_id", "schedule_id")
    def _compute_subject_name(self):
        for record in self.sudo().filtered("subject_id"):
            student_group = record.student_id.get_current_group(
                academic_year=record.academic_year_id)
            record.subject_name = record.subject_id.get_subject_name(
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
            "numeric_mark": 0.0,
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
    def button_set_pending(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": "pending",
        })

    @api.multi
    def button_remove_exceptionality(self):
        self.filtered(lambda r: r.state == "initial").write({
            "exceptionality": False,
        })

    @api.multi
    def button_show_records(self):
        self.ensure_one()
        records = self.child_record_ids
        if self.env.context.get("retake", False):
            records = self.retake_record_ids
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update(
            {"default_parent_record_id": self.id})
        domain = expression.AND([
            [("id", "in", records.ids)], safe_eval(action.domain or "[]")])
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
                 "child_record_ids.state",
                 "child_record_ids.retake_record_ids",
                 "child_record_ids.retake_record_ids.state",
                 "child_record_ids.retake_record_ids.numeric_mark")
    def _compute_generate_marks(self):
        for record in self:
            mark_records = record.child_record_ids.filtered(
                lambda r: r.state == "assessed" and
                r.exceptionality not in ["not_evaluated"] and
                not r.recovered_record_id)
            if mark_records:
                record.calculated_numeric_mark = sum(
                    [(x.get_max_numeric_mark(assessed=True) *
                      x.exam_eval_percent / 100)
                     for x in mark_records])

    @api.multi
    def is_partial_assessed(self):
        self.ensure_one()
        if self.child_record_ids:
            return any(x.is_partial_assessed() for x in self.child_record_ids)
        elif (self.state == "assessed" or
              self.exceptionality in ["not_taken", "not_evaluated"] or (
                not self.exam_id and self.numeric_mark != 0)):
            return True
        return False

    @api.multi
    def get_max_numeric_mark(self, assessed=False):
        self.ensure_one()
        retake_records = self.mapped("retake_record_ids")
        if assessed:
            retake_records = retake_records.filtered(
                lambda r: r.state == "assessed")
        numeric_mark_list = (
            [self.numeric_mark] + retake_records.mapped("numeric_mark"))
        return max(numeric_mark_list)

    @api.multi
    @api.depends("numeric_mark", "child_record_ids",
                 "child_record_ids.numeric_mark",
                 "child_record_ids.calculated_partial_mark",
                 "child_record_ids.exam_eval_percent",
                 "child_record_ids.state",
                 "child_record_ids.exceptionality",
                 "child_record_ids.retake_record_ids",
                 "child_record_ids.retake_record_ids.numeric_mark")
    def _compute_partial_marks(self):
        for record in self:
            mark_records = record.child_record_ids
            partial_mark = eval_percent = 0.0
            for mark_record in mark_records.filtered(
                    lambda r: r.exceptionality not in ["not_evaluated"] and
                    not r.recovered_record_id):
                if mark_record.is_partial_assessed():
                    eval_percent += mark_record.exam_eval_percent
                    partial_mark += (
                        ((mark_record.get_max_numeric_mark() or
                          mark_record.calculated_partial_mark)
                         if mark_record.exceptionality != "not_taken" else 0) *
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

    @api.multi
    def action_retake(self):
        new_records = self.env["education.record"]
        for record in self.filtered(
                lambda r: r.state == "assessed" and not r.exam_id):
            new_records |= record.copy(default={
                "recovered_record_id": record.id,
                "behaviour_mark_id": record.behaviour_mark_id.id,
            })
        return new_records

    @api.multi
    def action_round_numeric_mark(self):
        sys_params = self.env["ir.config_parameter"].sudo()
        precision = int(sys_params.get_param(
            "education.record.mark_precision", 0))
        for record in self.filtered(
                lambda r: r.competence_eval_mode != "behaviour"):
            record.numeric_mark = round(
                record.numeric_mark + 0.00001, precision)

    @api.multi
    def button_retake(self):
        self.ensure_one()
        records = self.action_retake()
        if not records:
            return False
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        action_dict.update({
            "res_id": records and records[:1].id,
            "views": [
                (self.env.ref("education_evaluation_notebook."
                              "education_record_view_form").id, 'form')]
        })
        return action_dict

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
            name = _("{} - {}").format(record.n_line_id.display_name,
                                       record.student_id.display_name)
            if record.recovered_record_id:
                name = _("[RETAKE] {}").format(name)
            result.append((record.id, name))
        return result
