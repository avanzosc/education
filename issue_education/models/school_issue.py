# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SchoolIssue(models.Model):
    _name = 'school.issue'
    _description = 'School issues'

    name = fields.Char(string='Description', required=True)
    school_issue_type_id = fields.Many2one(
        string='School issue type', comodel_name='school.college.issue.type',
        required=True)
    school_id = fields.Many2one(
        comodel_name='res.partner', name='Education Center',
        related='school_issue_type_id.school_id', store=True)
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type',
        related='school_issue_type_id.issue_type_id')
    requires_justification = fields.Boolean(
        string='Requires Justification')
    affect_to = fields.Selection(
        string='Affect to', selection=[('group', 'Group'),
                                       ('student', 'Student')])
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        domain=[('educational_category', '=', 'student')])
    reported_id = fields.Many2one(
        string='Reported by', comodel_name='res.users', required=True,
        default=lambda self: self.env.user)
    site_id = fields.Many2one(
        string='Site', comodel_name='school.issue.site')
    requires_imparting_group = fields.Boolean(
        string='Requires imparting group')
    group_id = fields.Many2one(
        string='Education group', comodel_name='education.group')
    issue_date = fields.Date(
        string='Date', required=True,
        default=lambda self: fields.Date.context_today(self))
    proof_id = fields.Many2one(
        string='Proof', comodel_name='school.issue.proof')
    education_schedule_id = fields.Many2one(
        string='Class Schedule', comodel_name='education.schedule')
    claim_id = fields.Many2one(
        string='Issue Report', comodel_name='school.claim')
    notes = fields.Text(string='Notes')
    proof_state = fields.Selection(
        selection=[
            ('required', 'Proof Required'),
            ('optional', 'No Proof Required'),
            ('proved', 'Proof Added'),
        ], string='Proving State', compute='_compute_proof_state', store=True)
    student_group_id = fields.Many2one(
        comodel_name="education.group", string="Student Official Group")

    @api.multi
    @api.depends('proof_id', 'requires_justification')
    def _compute_proof_state(self):
        for issue in self:
            if issue.proof_id:
                issue.proof_state = 'proved'
            else:
                if issue.requires_justification:
                    issue.proof_state = 'required'
                else:
                    issue.proof_state = 'optional'

    @api.onchange('school_issue_type_id')
    def onchange_school_issue_type_id(self):
        for issue in self:
            itype = issue.school_issue_type_id.issue_type_id
            issue.affect_to = itype.affect_to
            issue.requires_justification = itype.requires_justification

    @api.onchange('site_id')
    def onchange_site_id(self):
        for issue in self:
            issue.requires_imparting_group = (
                issue.site_id.requires_imparting_group)

    @api.onchange("student_id")
    def onchange_student_id(self):
        for issue in self:
            issue.student_group_id = issue.student_id.current_group_id

    @api.model
    def create(self, values):
        issues = super(SchoolIssue, self).create(values)
        for issue in issues.filtered('issue_type_id.generate_part'):
            issue.create_issue_report()
        return issues

    def create_issue_report(self):
        self.ensure_one()
        claim_obj = self.env['school.claim']
        claim_data = [
            ('school_issue_type_id', '=', self.school_issue_type_id.id),
            ('student_id', '=', self.student_id.id),
            ('education_group_id', '=', self.group_id.id),
            ('education_schedule_id', '=', self.education_schedule_id.id),
            ('state', '=', 'draft'),
        ]
        claim = claim_obj.search(claim_data)
        if claim:
            self.claim_id = claim
        else:
            values = self._catch_values_for_generate_part()
            self.claim_id = claim_obj.create(values)

    def _catch_values_for_generate_part(self):
        self.ensure_one()
        values = {
            'school_issue_id': self.id,
            'name': self.name,
            'issue_date': self.issue_date,
            'reported_id': self.reported_id.id,
            'school_issue_type_id': self.school_issue_type_id.id,
            'student_id': self.student_id.id,
            'education_group_id': self.group_id.id,
            'education_schedule_id': self.education_schedule_id.id,
        }
        return values
