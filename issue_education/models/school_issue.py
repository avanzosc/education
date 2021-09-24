# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SchoolIssue(models.Model):
    _name = 'school.issue'
    _description = 'School issues'
    _inherit = 'mail.thread'

    name = fields.Char(string='Description', required=True)
    school_issue_type_id = fields.Many2one(
        string='School issue type', comodel_name='school.college.issue.type',
        required=True)
    school_id = fields.Many2one(
        comodel_name='res.partner', name='Education Center',
        related='school_issue_type_id.school_id', store=True)
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type',
        related='school_issue_type_id.issue_type_id', store=True)
    gravity_scale_id = fields.Many2one(
        string='Severity scale', comodel_name='school.issue.severity.scale',
        related='school_issue_type_id.issue_type_id.gravity_scale_id',
        store=True)
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
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year", string="Academic Year",
        compute="_compute_academic_year", store=True)
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
    student_course_id = fields.Many2one(
        comodel_name="education.course", string="Course",
        related="student_group_id.course_id", store=True)
    student_level_id = fields.Many2one(
        comodel_name="education.level", string="Education Level",
        related="student_group_id.level_id", store=True)

    @api.depends("issue_date")
    def _compute_academic_year(self):
        academic_year_obj = self.env["education.academic_year"]
        for claim in self:
            claim.academic_year_id = academic_year_obj.search([
                ("date_start", "<=", claim.issue_date),
                ("date_end", ">=", claim.issue_date),
            ], limit=1)

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

    @api.multi
    def unlink(self):
        claims = self.mapped("claim_id")
        claims.filtered(lambda c: len(c.school_issue_ids) == 1).unlink()
        return super(SchoolIssue, self).unlink()

    def create_issue_report(self):
        self.ensure_one()
        if not self.claim_id:
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

    def open_issue_report(self):
        reports = self.mapped("claim_id")
        action = self.env.ref("issue_education.action_school_claim")
        action_dict = action.read()[0] if action else {}
        if len(reports) > 1:
            action_dict["domain"] = [("id", "in", reports.ids)]
        elif reports:
            form_view = [
                (self.env.ref("issue_education.school_claim_view_form").id,
                 "form")]
            if "views" in action:
                action_dict["views"] = form_view + [
                    (state, view) for state, view in action_dict["views"]
                    if view != "form"]
            else:
                action_dict["views"] = form_view
            action_dict["res_id"] = reports.id
        return action_dict

    def _catch_values_for_generate_part(self):
        self.ensure_one()
        values = {
            'school_issue_id': self.id,
            'name': self.name,
            'issue_date': self.issue_date,
            'reported_id': self.reported_id.id,
            'school_issue_type_id': self.school_issue_type_id.id,
            'student_id': self.student_id.id,
            'student_group_id': self.student_group_id.id,
            'education_group_id': self.group_id.id,
            'education_schedule_id': self.education_schedule_id.id,
        }
        return values
