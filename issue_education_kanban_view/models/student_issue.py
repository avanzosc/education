# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class StudentIssue(models.Model):
    _name = 'student.issue'
    _description = 'Student issues'

    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner')
    education_schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule')
    college_issue_type_id = fields.Many2one(
        string='College issue type', comodel_name='school.college.issue.type')
    name = fields.Char(
        string='Description', related='college_issue_type_id.name')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type',
        related='college_issue_type_id.issue_type_id')
    issue_count = fields.Integer(string='Count')
    issues_on_day = fields.Integer(
        string='Issues on day', default=0)
    image = fields.Binary(
        string='Image', attachment=True)
