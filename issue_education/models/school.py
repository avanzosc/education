# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, exceptions, _


class SchoolIssueSeverityScale(models.Model):
    _name = 'school.issue.severity.scale'
    _description = 'Issues severity scales'

    name = fields.Char(string='Description', required=True)
    gravity_scale = fields.Selection(
        string='Severity scale',
        selection=[('0', _(' 0(No evaluate)')),
                   ('-1', _('-1(Slight)')),
                   ('-2', _('-2(Significant)')),
                   ('-3', _('-3(Serious)')),
                   ('-4', _('-4(Very serious)')),
                   ('1', _(' 1(Positive)')),
                   ('2', _(' 2(Very positive)'))])

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            deno = dict(self.env['school.issue.severity.scale']._fields[
                'gravity_scale'].selection)[record.gravity_scale]
            result.append((record.id, '{}  {}'.format(record.name, deno)))
        return result


class SchoolIssueType(models.Model):
    _name = 'school.issue.type'
    _description = 'Types of issues'

    name = fields.Char(string='Description', required=True)
    affect_to = fields.Selection(
        string='Affect to',
        selection=[('group', 'Group'),
                   ('student', 'Student')])
    gravity_scale_id = fields.Many2one(
        string='Severity scale', comodel_name='school.issue.severity.scale')
    send_email = fields.Boolean(string='Send email', default=False)
    generate_part = fields.Boolean(string='Generate part', default=False)
    site_id = fields.Many2one(
        string='Site', comodel_name='school.issue.site')
    usual_issue = fields.Boolean(string='Usual issue')
    requires_justification = fields.Boolean(string='Requires Justification')
    notify_personal_tutor = fields.Boolean(
        string='Notify to personal tutor', default=True)
    notify_group_tutor = fields.Boolean(
        string='Notify to group tutor', default=True)
    other_managers = fields.One2many(
        string='Other managers', comodel_name='education.position',
        inverse_name='issue_level_id')
    image = fields.Binary(string='Image', attachment=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            gravity_scale = record.gravity_scale_id.gravity_scale
            deno = dict(self.env['school.issue.severity.scale']._fields[
                'gravity_scale'].selection)[gravity_scale]
            result.append((record.id, '{}  {}'.format(record.name, deno)))
        return result

    @api.multi
    def unlink(self):
        types = self.env['school.issue.type']
        types += self.env.ref('issue_education.schoolwork_issue_type_master')
        types += self.env.ref('issue_education.comes_late_issue_type_master')
        types += self.env.ref('issue_education.assistance_issue_type_master')
        types += self.env.ref('issue_education.uniformed_issue_type_master')
        types += self.env.ref('issue_education.small_fault_issue_type_master')
        for mtype in self:
            if mtype.id in types.ids:
                raise exceptions.Warning(
                    _('You cannot delete an issue type created by the system.')
                    )
        return super(SchoolIssueType, self).unlink()


class SchoolIssueSite(models.Model):
    _name = 'school.issue.site'
    _description = 'Issues sites'

    name = fields.Char(string='Description', required=True)
    requires_imparting_group = fields.Boolean(
        string='Requires imparting group', default=False)

    @api.multi
    def unlink(self):
        msite = self.env.ref('issue_education.classroom_school_issue_site')
        for site in self:
            if site.id == msite.id:
                raise exceptions.Warning(
                    _('You cannot delete an issue site created by the system.')
                    )
        return super(SchoolIssueSite, self).unlink()


class SchoolCollegeIssueType(models.Model):
    _name = 'school.college.issue.type'
    _description = 'Types of issues for colleges'
    _order = 'company_id, school_id, sequence'

    name = fields.Char(string='Description', required=True)
    sequence = fields.Integer(string='Sequence')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type')
    education_level_id = fields.Many2one(
        string='Level', comodel_name='education.level')
    school_id = fields.Many2one(
        comodel_name='res.partner', name='School',
        domain=[('educational_category', '=', 'school')])
    company_id = fields.Many2one(
        comodel_name='res.company', name='Company',
        related='school_id.company_id', store=True)
    educational_measure_ids = fields.Many2many(
        comodel_name='school.college.educational.measure',
        string='Educational measures', column1='school_issue_type_id',
        column2='school_educational_measure_id',
        relation='rel_school_issue_type_educational_measure')
    notify_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Notify to', column1='school_issue_type_id',
        column2='partner_id',
        relation='rel_school_issue_type_partner')
    image = fields.Binary(string='Image', attachment=True)

    @api.onchange('issue_type_id')
    def onchange_issue_type_id(self):
        if self.issue_type_id:
            self.name = self.issue_type_id.name
            self.image = self.issue_type_id.image

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            gravity_scale = record.issue_type_id.gravity_scale_id.gravity_scale
            deno = dict(self.env['school.issue.severity.scale']._fields[
                'gravity_scale'].selection)[gravity_scale]
            result.append((record.id, '{} - {}  {}'.format(
                record.school_id.name, record.name, deno)))
        return result


class SchoolCollegeEducationalMeasure(models.Model):
    _name = 'school.college.educational.measure'
    _description = 'Educational measures'

    name = fields.Char(string='Description', required=True)
    school_id = fields.Many2one(
        comodel_name='res.partner', name='School',
        domain=[('educational_category', '=', 'school')])
    company_id = fields.Many2one(
        comodel_name='res.company', name='Company',
        related='school_id.company_id', store=True)
    severity_level_id = fields.Many2one(
        comodel_name='school.issue.severity.scale', name='Severity level')


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
    school_issue_type_id = fields.Many2one(
        string='School issue type', comodel_name='school.college.issue.type')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type')
    requires_justification = fields.Boolean(
        string='Requires Justification')
    affect_to = fields.Selection(
        string='Affect to', selection=[('group', 'Group'),
                                       ('student', 'Student')])
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        domain=[('educational_category', '=', 'student')])
    reported_id = fields.Many2one(
        string='Reported by', comodel_name='res.users')
    site_id = fields.Many2one(
        string='Site', comodel_name='school.issue.site')
    requires_imparting_group = fields.Boolean(
        string='Requires imparting group')
    impartation_group_id = fields.Many2one(
        string='Impartation group', comodel_name='education.group')
    issue_date = fields.Date(string='Date', required=True)
    proof_id = fields.Many2one(
        string='Proof', comodel_name='school.issue.proof')

    @api.onchange('school_issue_type_id')
    def onchange_school_issue_type_id(self):
        for issue in self.filtered(lambda c: c.school_issue_type_id):
            issue.issue_type_id = issue.school_issue_type_id.issue_type_id.id
            itype = issue.school_issue_type_id.issue_type_id
            issue.requires_justification = itype.requires_justification
            issue.affect_to = itype.affect_to

    @api.onchange('site_id')
    def onchange_site_id(self):
        for issue in self.filtered(lambda c: c.site_id):
            issue.requires_imparting_group = (
                issue.site_id.requires_imparting_group)
