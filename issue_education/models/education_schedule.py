# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationSchedule(models.Model):
    _inherit = "education.schedule"

    @api.multi
    def button_open_school_issues(self):
        self.ensure_one()
        action = self.env.ref("issue_education.action_school_issue")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update({
            "default_education_schedule_id": self.id,
        })
        domain = expression.AND([
            [("student_id", "in", self.mapped('student_ids').ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def button_open_school_claims(self):
        self.ensure_one()
        action = self.env.ref("issue_education.action_school_claim")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update({
            "default_education_schedule_id": self.id,
        })
        domain = expression.AND([
            [("student_id", "in", self.mapped('student_ids').ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
