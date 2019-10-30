# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


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
        related='site_id.requires_imparting_group')
    group_id = fields.Many2one(
        string='Education Group', comodel_name='education.group')
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
        context = self.env.context
        res = super(WizCreateIssue, self).default_get(var_fields)
        student_id = context.get('active_id')
        group_id = context.get('education_group_id')
        scheduled_id = context.get('education_schedule_id')
        school_id = context.get('school_id')
        if not group_id and scheduled_id:
            schedule = self.env['education.schedule'].browse(scheduled_id)
            group_id = schedule.group_ids.filtered(
                lambda g: student_id in g.student_ids.ids)[:1].id
        if not school_id and student_id:
            student = self.env['res.partner'].browse(student_id)
            school_id = student.current_center_id.id
        res.update({
            'student_id': student_id,
            'education_schedule_id': scheduled_id,
            'group_id': group_id,
            'school_id': school_id,
        })
        return res

    # @api.onchange('school_issue_type_id')
    # def onchange_school_issue_type_id(self):
    #     for issue in self.filtered(lambda c: c.school_issue_type_id):
    #         itype = issue.school_issue_type_id.issue_type_id
    #         issue.requires_justification = itype.requires_justification
    #         issue.affect_to = itype.affect_to
    #         if issue.education_schedule_id:
    #             n = _('School: {}, Education subject: {}, Session: {}').format(
    #                 issue.education_schedule_id.center_id.name,
    #                 issue.education_schedule_id.subject_id.description,
    #                 issue.education_schedule_id.session_number)
    #         else:
    #             n = _('School: {}, Issue type: {}').format(
    #                 self.school_id.name, self.school_issue_type_id.name)
    #         issue.name = n
    #         if itype.site_id:
    #             issue.site_id = itype.site_id.id
                # issue.requires_imparting_group = (
                #     itype.site_id.requires_imparting_group)

    # @api.onchange('site_id')
    # def onchange_site_id(self):
    #     for issue in self.filtered(lambda c: c.site_id):
    #         issue.requires_imparting_group = (
    #             issue.site_id.requires_imparting_group)

    @api.multi
    def create_issue(self):
        vals = self.prepare_vals_for_create_issue()
        self.env['school.issue'].create(vals)
        # if issue.issue_type_id.generate_part:
        #     issue._generate_part()
        # Close wizard and reload view
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }

    def prepare_vals_for_create_issue(self):
        vals = {
            'name': self.name,
            'student_id': self.student_id.id,
            'school_issue_type_id': self.school_issue_type_id.id,
            'issue_type_id': self.school_issue_type_id.issue_type_id.id,
            'requires_justification': self.requires_justification,
            'affect_to': self.affect_to,
            'reported_id': self.reported_id.id,
            'requires_imparting_group': self.requires_imparting_group,
            'issue_date': self.issue_date,
            'claim_id': self.claim_id.id,
        }
        if self.site_id:
            vals['site_id'] = self.site_id.id
        if self.group_id:
            vals['group_id'] = self.group_id.id
        if self.claim_id:
            vals['claim_id'] = self.claim_id.id
        if self.proof_id:
            vals['proof_id'] = self.proof_id.id
        if self.education_schedule_id:
            vals['education_schedule_id'] = self.education_schedule_id.id
        return vals
