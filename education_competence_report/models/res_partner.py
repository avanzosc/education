# Copyright 2023 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def button_open_criteria_report(self):
        self.ensure_one()
        action = self.env.ref(
            "education_competence_report."
            "education_student_criteria_report_student_action")
        action_dict = action.read()[0] if action else {}
        domain = [
            ("student_id", "=", self.id),
        ]
        action_dict.update({
            "domain": domain,
        })
        return action_dict
