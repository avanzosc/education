# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class WizCreateAssistanceIssue(models.TransientModel):
    _inherit = "wiz.create.assistance.issue"

    @api.multi
    def create_assistance_issues(self):
        action_dict = super(WizCreateAssistanceIssue, self).create_assistance_issues()
        low_wizard = self.env["fleet.route.support.batch.wizard"].create({
            #"partner_ids": self.partner_ids.ids,
            "type": "low",
            "date": self.date,
            "low_type": "lack of assistance",
            "direction": "both",
        })
        low_wizard.create_issues()
        return action_dict
