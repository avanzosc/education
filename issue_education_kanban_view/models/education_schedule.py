# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api, _


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

    @api.multi
    def button_generate_view_issues(self):
        self.ensure_one()
        cond = [('education_schedule_id', '=', self.id),
                ('student_id', 'in', self.student_ids.ids)]
        issues = self.env['student.issue'].search(cond)
        if issues:
            issues.unlink()
        context = self.env.context.copy()
        context.update({
            'education_schedule': self.id,
            'school_id': self.center_id.id,
        })
        if 'group_by' in context:
            context.pop('group_by')
        compose_kanban = self.env.ref(
            'issue_education_kanban_view.res_partner_issue_view_kanban')
        return {
            'name': _('Issues'),
            'type': 'ir.actions.act_window',
            'view_type': 'kanban',
            'view_mode': 'kanban',
            'res_model': 'res.partner',
            'views': [(compose_kanban.id, 'kanban')],
            'view_id': compose_kanban.id,
            'context': context,
            'domain': [('id', 'in', self.student_ids.ids)]}
