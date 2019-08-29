# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_student_issue_ids(self):
        today = fields.Date.context_today(self)
        for student in self:
            cond = []
            if self.env.context.get('school_id', False):
                cond = [('school_id', '=', self.env.context.get('school_id'))]
            else:
                if student.current_center_id:
                    cond = [('school_id', '=', student.current_center_id.id)]
            types = []
            if cond:
                types = self.env['school.college.issue.type'].search(
                    cond, limit=5, order='sequence')
            student_issues = self.env['student.issue']
            for mtype in types:
                cond = [('school_issue_type_id', '=', mtype.id),
                        ('student_id', '=', student.id)]
                issues = self.env['school.issue'].search(cond)
                issues2 = issues.filtered(lambda c: c.issue_date < today)
                vals = {'student_id': student.id,
                        'education_schedule_id':
                        self.env.context.get('education_schedule', False),
                        'college_issue_type_id': mtype.id,
                        'issue_count': len(issues2),
                        'issues_on_day': 0}
                if len(issues) > 0:
                    issues = issues.filtered(lambda c: c.issue_date == today)
                    if len(issues) > 0:
                        vals['issues_on_day'] = len(issues)
                issue = self.env['student.issue'].create(vals)
                if mtype.image:
                    issue.image = mtype.image
                student_issues += issue
            if student_issues:
                student.student_issue_ids = [(6, 0, student_issues.ids)]

    def _compute_student_issue_ids2(self):
        for student in self:
            student.student_issue_ids2 = student.student_issue_ids

    school_issue_ids = fields.One2many(
        string='Issues', comodel_name='school.issue',
        inverse_name='student_id')
    student_issue_ids = fields.Many2many(
        string='Student issues', comodel_name='student.issue',
        compute='_compute_student_issue_ids')
    student_issue_ids2 = fields.One2many(
        string='Student issues', comodel_name='student.issue',
        compute='_compute_student_issue_ids2')
