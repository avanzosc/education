# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class WizCreateIssue(models.TransientModel):
    _name = "wiz.create.issue"
    _description = "Wizard for create issues"

    name = fields.Char(string='Description', required=True)
    requires_justification = fields.Boolean(
        string='Requires Justification')
    school_issue_type_id = fields.Many2one(
        string='School issue type', comodel_name='school.college.issue.type')
    school_id = fields.Many2one(
        string='School', comodel_name='res.partner')
    affect_to = fields.Selection(
        string='Affect to', selection=[('group', 'Group'),
                                       ('student', 'Student')])
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        domain=[('educational_category', '=', 'student')])
    reported_id = fields.Many2one(
        string='Reported by', comodel_name='res.users',
        default=lambda self: self.env.user.id)
    site_id = fields.Many2one(
        string='Site', comodel_name='school.issue.site')
    requires_imparting_group = fields.Boolean(
        string='Requires imparting group')
    impartation_group_id = fields.Many2one(
        string='Impartation group', comodel_name='education.group')
    issue_date = fields.Date(
        string='Date', required=True,
        default=lambda self: fields.Date.context_today(self))
    claim_id = fields.Many2one(
        string='Claim', comodel_name='crm.claim')
    proof_id = fields.Many2one(
        string='Proof', comodel_name='school.issue.proof')
    education_schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule')

    @api.model
    def default_get(self, var_fields):
        res = super(WizCreateIssue, self).default_get(var_fields)
        student = self.env['res.partner'].browse(
            self.env.context.get('active_id'))
        res.update({'student_id': student.id,
                    'school_id': self.env.context.get('school_id')})
        if self.env.context.get('education_schedule', False):
            res.update({'education_schedule_id':
                        self.env.context.get('education_schedule')})
        if self.env.context.get('school_id', False):
            res.update({'school_id': self.env.context.get('school_id')})
        else:
            res.update({'school_id': student.current_center_id.id})
        return res

    @api.onchange('school_issue_type_id')
    def onchange_school_issue_type_id(self):
        for issue in self.filtered(lambda c: c.school_issue_type_id):
            itype = issue.school_issue_type_id.issue_type_id
            issue.requires_justification = itype.requires_justification
            issue.affect_to = itype.affect_to
            if issue.education_schedule_id:
                n = _('School: {}, Education subject: {}, Session: {}').format(
                    issue.education_schedule_id.center_id.name,
                    issue.education_schedule_id.subject_id.description,
                    issue.education_schedule_id.session_number)
            else:
                n = _('School: {}, Issue type: {}').format(
                    self.school_id.name, self.school_issue_type_id.name)
            issue.name = n
            if itype.site_id:
                issue.site_id = itype.site_id.id
                issue.requires_imparting_group = (
                    itype.site_id.requires_imparting_group)

    @api.onchange('site_id')
    def onchange_site_id(self):
        for issue in self.filtered(lambda c: c.site_id):
            issue.requires_imparting_group = (
                issue.site_id.requires_imparting_group)

    @api.multi
    def create_issue(self):
        vals = self.prepare_vals_for_create_issue()
        issue = self.env['school.issue'].create(vals)
        if issue.issue_type_id.generate_part:
            issue._generate_part()
        if self.education_schedule_id:
            return self.education_schedule_id.button_generate_view_issues()

    def prepare_vals_for_create_issue(self):
        vals = {
            'name': self.name,
            'school_issue_type_id': self.school_issue_type_id.id,
            'issue_type_id': self.school_issue_type_id.issue_type_id.id,
            'requires_justification': self.requires_justification,
            'affect_to': self.affect_to,
            'student_id': self.student_id.id,
            'reported_id': self.reported_id.id,
            'requires_imparting_group': self.requires_imparting_group,
            'issue_date': self.issue_date}
        if self.site_id:
            vals['site_id'] = self.site_id.id
        if self.impartation_group_id:
            vals['impartation_group_id'] = self.impartation_group_id.id
        if self.claim_id:
            vals['claim_id'] = self.claim_id.id
        if self.proof_id:
            vals['proof_id'] = self.proof_id.id
        if self.education_schedule_id:
            vals['education_schedule_id'] = self.education_schedule_id.id
        return vals
