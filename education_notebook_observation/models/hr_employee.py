# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    notebook_observation_ids = fields.One2many(
        string='Notebook observations', inverse_name='teacher_id',
        comodel_name='education.notebook.observation')
    count_notebook_observation = fields.Integer(
        string='# Notebook observations',
        compute='_compute_count_notebook_observation')

    @api.multi
    def _compute_count_notebook_observation(self):
        for employee in self:
            employee.count_notebook_observation = len(
                employee.notebook_observation_ids)

    @api.multi
    def button_show_notebook_observations(self):
        self.ensure_one()
        action = self.env.ref('education_notebook_observation.education_'
                              'notebook_observation_action')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update({
            'search_default_teacher_id': self.id,
            'default_teacher_id': self.id,
        })
        domain = expression.AND([
            [('teacher_id', 'in', self.ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict
