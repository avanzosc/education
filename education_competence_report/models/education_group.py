# Copyright 2022 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class EducationGroup(models.Model):
    _inherit = 'education.group'

    @api.multi
    def button_open_group_competences(self):
        action = self.env.ref('education_competence_report.action_education_competence_from_group')
        action_dict = action.read()[0] if action else {}
        domain = [('group_id', '=', self.id)]
        action_dict.update({
            'domain': domain,
        })
        return action_dict

