# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class StudentIssue(models.Model):
    _name = 'student.issue'
    _description = 'Student issues'
    _order = 'sequence'

    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner', required=True,
        ondelete='cascade')
    education_schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule')
    college_issue_type_id = fields.Many2one(
        string='College issue type', comodel_name='school.college.issue.type')
    sequence = fields.Integer(
        string='Sequence', related='college_issue_type_id.sequence')
    name = fields.Char(
        string='Description', related='college_issue_type_id.name')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type',
        related='college_issue_type_id.issue_type_id')
    issue_count = fields.Integer(
        string='Count', compute='_compute_issue_count')
    issues_on_day = fields.Integer(
        string='Issues on day', compute='_compute_issue_count')

    def _compute_issue_count(self):
        today = fields.Date.context_today(self)
        issue_model = self.env['school.issue']
        for student_issue in self:
            school_issues = issue_model.search([
                ('student_id', '=', student_issue.student_id.id),
                ('school_issue_type_id', '=',
                 student_issue.college_issue_type_id.id),
            ])
            if student_issue.education_schedule_id:
                school_issues.filtered(
                    lambda i: i.education_schedule_id ==
                    student_issue.education_schedule_id)
            student_issue.issue_count = len(
                school_issues.filtered(lambda i: i.issue_date < today))
            student_issue.issues_on_day = len(
                school_issues.filtered(lambda i: i.issue_date == today))
