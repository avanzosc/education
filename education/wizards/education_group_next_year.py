# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationGroupNextYear(models.TransientModel):
    _name = "education.group.next_year"
    _description = "Wizard to create next academic year official groups"

    def create_next_year_groups(self):
        current_groups = self.env["education.group"].search([
            ("academic_year_id.current", "=", True),
            ("group_type_id.type", "=", "official"),
        ])
        groups = current_groups.create_next_academic_year()
        action = self.env.ref("education.action_education_group")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict["context"].update({
            "search_default_current_academic_year": False,
        })
        domain = expression.AND([
            [("id", "in", groups.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
