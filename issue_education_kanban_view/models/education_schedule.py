# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

    @api.multi
    def button_generate_view_issues(self):
        self.ensure_one()
        action = self.env.ref(
            'issue_education_kanban_view.res_partner_education_issue_action')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update({
            'education_schedule_id': self.id,
            'school_id': self.center_id.id,
        })
        domain = expression.AND([
            [('id', 'in', self.student_ids.ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict
