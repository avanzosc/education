# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    academic_record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="student_id",
        string="Academic Records")
    academic_record_count = fields.Integer(
        string="# Academic Record", compute="_compute_academic_record_count")

    @api.multi
    @api.depends("academic_record_ids")
    def _compute_academic_record_count(self):
        for partner in self.filtered("academic_record_ids"):
            partner.academic_record_count = len(partner.academic_record_ids)

    @api.multi
    def button_show_student_records(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("student_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def get_academic_records(self, academic_year, eval_type=False):
        self.ensure_one()
        if not eval_type:
            eval_obj = self.env["education.academic_year.evaluation"]
            evaluation = eval_obj.search([
                ("current", "=", True),
                ("center_id", "=", self.current_center_id.id),
                ("course_id", "=", self.current_course_id.id),
            ], limit=1)
            eval_type = evaluation.eval_type or "final"
        return self.academic_record_ids.filtered(
            lambda r: r.eval_type == eval_type and
            r.academic_year_id == academic_year and
            (r.evaluation_competence or r.global_competence))

    @api.multi
    def get_academic_records_curricular(self, academic_year, eval_type=False):
        self.ensure_one()
        academic_records = self.get_academic_records(
            academic_year, eval_type=eval_type)
        return academic_records.filtered(
            lambda r:
            r.n_line_id.schedule_id.task_type_id.education_code == "0120" and
            not r.recovered_record_id)

    @api.multi
    def get_academic_records_teaching(self, academic_year, eval_type=False):
        self.ensure_one()
        academic_records = self.get_academic_records(
            academic_year, eval_type=eval_type)
        return academic_records.filtered(
            lambda r:
            r.n_line_id.schedule_id.task_type_id.education_code == "0105")

    @api.multi
    def get_academic_records_non_curricular(
            self, academic_year, eval_type=False):
        self.ensure_one()
        academic_records = self.get_academic_records(
            academic_year, eval_type=eval_type)
        return academic_records.filtered(
            lambda r:
            r.n_line_id.schedule_id.task_type_id.education_code == "0123")

    @api.multi
    def get_notebook_lines(self, academic_year=False, eval_type=False):
        self.ensure_one()
        notebook_lines = self.env["education.notebook.line"]
        if not academic_year:
            academic_year = self.env["education.academic_year"].search([
                ("current", "=", True),
            ])
        groups = self.student_group_ids.filtered(
            lambda g: g.academic_year_id == academic_year)
        if not eval_type:
            group = groups.filtered(
                lambda g: g.group_type_id.type == "official")
            eval_obj = self.env["education.academic_year.evaluation"]
            evaluation = eval_obj.search([
                ("current", "=", True),
                ("academic_year_id", "=", academic_year.id),
                ("center_id", "=", group.center_id.id),
                ("course_id", "=", group.course_id.id),
            ], limit=1)
            eval_type = evaluation.eval_type or "final"
        for group in groups:
            notebook_lines |= group.get_notebook_lines(eval_type=eval_type)
        return notebook_lines
