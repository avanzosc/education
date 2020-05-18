# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def button_open_schedule(self):
        self.ensure_one()
        action = self.env.ref(
            "education.action_education_group_teacher_timetable_report")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("professor_id", "=", self.id)],
            safe_eval(action.domain or "[]")
        ])
        action_dict.update({
            "domain": domain,
        })
        return action_dict
