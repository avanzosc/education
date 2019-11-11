# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationGroup(models.Model):
    _inherit = 'education.group'

    @api.multi
    def button_generate_view_issues(self):
        self.ensure_one()
        action = self.env.ref(
            'issue_education_kanban_view.res_partner_education_issue_action')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update({
            'education_group_id': self.id,
            'school_id': self.center_id.id,
        })
        domain = expression.AND([
            [('id', 'in', self.student_ids.ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict
