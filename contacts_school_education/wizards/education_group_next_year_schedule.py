# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationGroupNextYear(models.TransientModel):
    _name = "education.group.next_year.schedule"
    _description = "Wizard to create next academic year groups schedule"

    def create_next_year_group_schedule(self):
        current_year = self.env["education.academic_year"].search([
            ("current", "=", True)
        ])
        next_year = current_year._get_next()
        next_year_groups = self.env["education.group"].search([
            ("academic_year_id", "=", next_year.id),
            ("group_type_id.type", "=", "official"),
        ])
        next_year_groups.create_schedule()
        action = self.env.ref("education.action_education_schedule")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update({
            "search_default_current_academic_year": False,
        })
        domain = expression.AND([
            [("academic_year_id", "=", next_year.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
