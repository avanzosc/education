# Copyright 2020 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationGroup(models.Model):
    _inherit = "education.group"

    record_count = fields.Integer(
        string="# Academic Records", compute="_compute_record_count")

    @api.multi
    @api.depends("student_ids", "student_ids.academic_record_ids")
    def _compute_record_count(self):
        academic_record_obj = self.env["education.record"]
        for group in self:
            group.record_count = academic_record_obj.search_count([
                ("student_id", "in", group.student_ids.ids),
                ("academic_year_id", "=", group.academic_year_id.id),
            ])

    @api.multi
    def button_show_records(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0]if action else {}
        domain = expression.AND([
            [("student_id", "in", self.student_ids.ids),
             ("academic_year_id", "=", self.academic_year_id.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({
            "domain": domain,
        })
        return action_dict

    @api.multi
    def get_notebook_lines(self, eval_type=False):
        self.ensure_one()
        notebook_obj = self.env["education.notebook.line"]
        if not eval_type:
            eval_obj = self.env["education.academic_year.evaluation"]
            evaluation = eval_obj.search([
                ("current", "=", True),
                ("academic_year_id", "=", self.academic_year_id.id),
                ("center_id", "=", self.center_id.id),
                ("course_id", "=", self.course_id.id),
            ], limit=1)
            eval_type = evaluation.eval_type or "final"
        return notebook_obj.search([
            ("eval_type", "=", eval_type),
            ("schedule_id.group_ids", "in", self.ids),
        ])
