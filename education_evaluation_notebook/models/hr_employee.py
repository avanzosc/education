# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def get_groups(self):
        self.ensure_one()
        groups = super(HrEmployee, self).get_groups()
        schedules = self.env["education.schedule"].search([
            ("teacher_id", "=", self.id)
        ])
        groups |= schedules.mapped("student_ids.student_group_ids")
        return groups

    @api.multi
    def button_open_group_exams(self):
        self.ensure_one()
        action = self.env.ref("education_evaluation_notebook."
                              "action_education_group_exam_report")
        action_dict = action.read()[0] if action else {}
        groups = self.get_groups()
        domain = expression.AND([
            [("group_id", "in", groups.ids)],
            safe_eval(action.domain or "[]")
        ])
        context = safe_eval(action.context or '{}')
        context.update({
            "search_default_teacher_id": self.id,
        })
        action_dict.update({
            "domain": domain,
            "context": context,
            "view_mode": "calendar,tree",
            "views": [(False, "calendar"), (False, "tree")],
        })
        return action_dict

    @api.multi
    def button_open_group_homework(self):
        self.ensure_one()
        action = self.env.ref("education_evaluation_notebook."
                              "action_education_group_homework_report")
        action_dict = action.read()[0] if action else {}
        groups = self.get_groups()
        domain = expression.AND([
            [("group_id", "in", groups.ids)],
            safe_eval(action.domain or "[]")
        ])
        context = safe_eval(action.context or '{}')
        context.update({
            "search_default_teacher_id": self.id,
        })
        action_dict.update({
            "domain": domain,
            "context": context,
            "view_mode": "calendar,tree",
            "views": [(False, "calendar"), (False, "tree")],
        })
        return action_dict
