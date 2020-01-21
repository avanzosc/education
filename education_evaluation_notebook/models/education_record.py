# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationRecord(models.Model):
    _name = "education.record"
    _description = "Academic Record"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]

    @api.model
    def _get_selection_exam_state(self):
        return self.env["education.exam"].fields_get(
            allfields=["state"])["state"]["selection"]

    @api.model
    def _get_selection_eval_type(self):
        return self.env["education.academic_year.evaluation"].fields_get(
            allfields=["eval_type"])["eval_type"]["selection"]

    exam_id = fields.Many2one(
        comodel_name="education.exam", string="Exam")
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
        related="competence_id.global_check",
        string="Global Competence", store=True)
    schedule_id = fields.Many2one(
        comodel_name="education.schedule", related="n_line_id.schedule_id",
        string="Class Schedule", store=True)
    subject_id = fields.Many2one(
        comodel_name="education.subject", string="Education Subject",
        related="n_line_id.schedule_id.subject_id", store=True)
    teacher_id = fields.Many2one(
        comodel_name="hr.employee", related="n_line_id.schedule_id.teacher_id",
        string="Teacher", store=True)
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        related="n_line_id.schedule_id.academic_year_id",
        string="Academic Year", store=True)
    evaluation_id = fields.Many2one(
        comodel_name="education.academic_year.evaluation",
        related="n_line_id.evaluation_id", string="Evaluation", store=True)
    eval_type = fields.Selection(
        selection="_get_selection_eval_type",
        related="n_line_id.eval_type",
        string="Evaluation Season", store=True)
    student_id = fields.Many2one(
        comodel_name="res.partner", string="Student", required=True)
    numeric_mark = fields.Float(string="Numeric Mark")
    behaviour_mark_id = fields.Many2one(
        comodel_name="education.mark.behaviour", string="Behaviour Mark")
    # competence_parent = fields.Many2one(
    #     related="n_line_id.parent_competence_id.competence_id",
    #     comodel_name="education.competence",
    #     store=True, string="parent competence")
    # competence_parent_parent = fields.Many2one(
    #     related="n_line_id.parent_competence_id.parent_competence_id."
    #             "competence_id",
    #     comodel_name="education.competence",
    #     store=True, string="parents parent competence")
    # master_competence_eval_check = fields.Boolean(
    #     string="Evaluation check for the competence",
    #     related="n_line_id.competence_id.evaluation_check")
    # master_competence_global_check = fields.Boolean(
    #     string="Global check for the competence",
    #     related="n_line_id.competence_id.global_check")
    calculated_numeric_mark = fields.Float(
        compute="_compute_generate_marks", string="Calculated Numeric Mark",
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

    @api.multi
    @api.depends("child_record_ids")
    def _compute_child_record_count(self):
        for record in self:
            record.child_record_count = len(record.child_record_ids)

    @api.multi
    @api.depends("numeric_mark")
    def _compute_mark_id(self):
        mark_obj = self.env["education.mark.numeric"]
        for record in self:
            record.mark_id = mark_obj.search([
                ("initial_mark", "<=", record.numeric_mark),
                ("final_mark", ">=", record.numeric_mark)], limit=1)

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
    @api.depends("numeric_mark")
    def _compute_mark_code(self):
        mark_obj = self.env["education.mark.numeric"]
        for record in self:
            record.mark_id = mark_obj.search([
                ("initial_mark", "<=", record.numeric_mark),
                ("final_mark", ">=", record.numeric_mark)], limit=1)

    @api.multi
    @api.depends("child_record_ids", "child_record_ids.numeric_mark",
                 "child_record_ids.exam_eval_percent")
    def _compute_generate_marks(self):
        for record in self:
            record.calculated_numeric_mark = sum(
                [x.numeric_mark * x.exam_eval_percent / 100
                 for x in record.child_record_ids])
