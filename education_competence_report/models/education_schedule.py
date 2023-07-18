# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

    @api.multi
    def button_open_schedule_criterias(self):
        action = self.env.ref('education_competence_report.action_education_schedule_criteria_from')
        action_dict = action.read()[0] if action else {}
        domain = [('schedule_id', '=', self.id)]
        action_dict.update({
            'domain': domain,
        })
        return action_dict

