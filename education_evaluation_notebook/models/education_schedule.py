# Copyright (c) 2019 Adrian Revilla <adrianrevilla@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'
    
    notebook_lines_count = fields.Integer(compute='_count_notebook_lines',
                                          string='Teacher notebook lines')
    
    def button_show_notebook_lines(self):
        notebook_lines = self.env['education.notebook.line'].search([(
            'planification_id', '=', self.id)])
        my_context = self.env.context.copy()
        my_context['default_planification_id'] = self.id
        my_context['search_default_planification_id'] = self.id
        return {
            'name': _('Teacher notebook lines'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.notebook.line',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', notebook_lines.ids)],
        }

    def _count_notebook_lines(self):
        self.notebook_lines_count = 0
        notebook_lines = self.env['education.notebook.line'].search([(
            'planification_id', '=', self.id)])
        self.notebook_lines_count = len(notebook_lines)