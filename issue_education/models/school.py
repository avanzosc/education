# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class SchoolIssueTypeMaster(models.Model):
    _name = 'school.issue.type.master'
    _description = 'Master types of issues'

    name = fields.Char(string='Description', required=True)
    affect_to = fields.Selection(
        string='Affect to',
        selection=[('group', 'Group'),
                   ('student', 'Student')])


class SchoolIssueSeverityLevel(models.Model):
    _name = 'school.issue.severity.level'
    _description = 'Issues severity levels'

    name = fields.Char(string='Description', required=True)
    gravity_scale = fields.Selection(
        string='Gravity level',
        selection=[('0', 'No evaluate'),
                   ('1', 'Positive'),
                   ('2', 'Very positive'),
                   ('-1', 'Slight'),
                   ('-2', 'Significant'),
                   ('-3', 'Serious'),
                   ('-4', 'Very serious')])
    notify_personal_tutor = fields.Boolean(
        string='Notify to personal tutor', default=True)
    notify_group_tutor = fields.Boolean(
        string='Notify to group tutor', default=True)
    other_managers = fields.One2many(
        string='Other managers', comodel_name='education.position',
        inverse_name='issue_level_id')


class SchoolIssueType(models.Model):
    _name = 'school.issue.type'
    _description = 'Types of issues'

    name = fields.Char(string='Description', required=True)
    send_email = fields.Boolean(string='Send email', default=False)
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type.master')
    generate_part = fields.Boolean(string='Generate part', default=False)
    severity_level_id = fields.Many2one(
        string='Severity level', comodel_name='school.issue.severity.level')
    usual_issue = fields.Boolean(string='Usual issue')
    requires_justification = fields.Boolean(string='Requires Justification')
    image = fields.Binary(string='Image', attachment=True)


class SchoolIssueSite(models.Model):
    _name = 'school.issue.site'
    _description = 'Issues sites'

    name = fields.Char(string='Description', required=True)
    requires_imparting_group = fields.Boolean(
        string='Requires imparting group', default=False)


class SchoolCollegeIssueType(models.Model):
    _name = 'school.college.issue.type'
    _description = 'Types of issues for colleges'
    _rec_name = 'own_name'

    sequence_id = fields.Many2one(
        string='Sequence', comodel_name='ir.sequence')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type')
    own_name = fields.Char(string='Own name', required=True)
    education_level_id = fields.Many2one(
        string='Level', comodel_name='education.level')
    school_id = fields.Many2one(
        comodel_name='res.partner', name='School',
        domain=[('educational_category', '=', 'school')])
    company_id = fields.Many2one(
        comodel_name='res.company', name='Company')

    @api.onchange('issue_type_id')
    def onchange_issue_type_id(self):
        if self.issue_type_id:
            self.own_name = self.issue_type_id.name


class SchoolCollegeEducationalMeasure(models.Model):
    _name = 'school.college.educational.measure'
    _description = 'Educational measures'

    name = fields.Char(string='Description', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company', name='Company')
    school_id = fields.Many2one(
        comodel_name='res.partner', name='School',
        domain=[('educational_category', '=', 'school')])
    severity_level_id = fields.Many2one(
        comodel_name='school.issue.severity.level', name='Severity level')


class SchoolIssueProof(models.Model):
    _name = 'school.issue.proof'
    _description = 'Issue proof'

    name = fields.Char(string='Description', required=True)
    person_id = fields.Many2one(
        comodel_name='res.partner', name='Progenitor/Tutor',
        domain=[('progenitor', 'Progenitor'),
                ('guardian', 'legal guardian')])


class SchoolIssue(models.Model):
    _name = 'school.issue'
    _description = 'School issues'

    name = fields.Char(string='Description', required=True)
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type')
    requires_justification = fields.Boolean(
        string='Requires Justification', store=True,
        related='issue_type_id.requires_justification')
    master_issue_type_id = fields.Many2one(
        string='Master issue type', comodel_name='school.issue.type.master',
        related='issue_type_id.issue_type_id', store=True)
    affect_to = fields.Selection(
        string='Affect to', selection=[('group', 'Group'),
                                       ('student', 'Student')],
        related='master_issue_type_id.affect_to', store=True)
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        domain=[('educational_category', '=', 'student')])
    reported_id = fields.Many2one(
        string='Reported by', comodel_name='res.users')
    site_id = fields.Many2one(
        string='Site', comodel_name='school.issue.site')
    requires_imparting_group = fields.Boolean(
        string='Requires imparting group',
        related='site_id.requires_imparting_group', store=True)
    impartation_group_id = fields.Many2one(
        string='Impartation group', comodel_name='education.group')
    issue_date = fields.Date(string='Date', required=True)
    claim_id = fields.Many2one(
        string='Claim', comodel_name='crm.claim')
    proof_id = fields.Many2one(
        string='Proof', comodel_name='school.issue.proof')
