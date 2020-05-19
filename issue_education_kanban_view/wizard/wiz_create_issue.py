# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizCreateIssue(models.TransientModel):
    _name = "wiz.create.issue"
    _description = "Wizard for create issues"

    @api.model
    def _get_selection_affect_to(self):
        return self.env['school.issue.type'].fields_get(
            allfields=['affect_to'])['affect_to']['selection']

    name = fields.Char(string='Description', required=True)
    notes = fields.Text(string='Notes')
    school_id = fields.Many2one(
        string='School', comodel_name='res.partner', required=True)
    school_issue_type_id = fields.Many2one(
        string='School issue type', comodel_name='school.college.issue.type')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type',
        related='school_issue_type_id.issue_type_id')
    requires_justification = fields.Boolean(
        string='Requires Justification',
        related='issue_type_id.requires_justification')
    affect_to = fields.Selection(
        string='Affect to', selection=_get_selection_affect_to,
        related='school_issue_type_id.affect_to')
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        domain=[('educational_category', '=', 'student')])
    reported_id = fields.Many2one(
        string='Reported by', comodel_name='res.users',
        default=lambda self: self.env.user.id)
    site_id = fields.Many2one(
        string='Site', comodel_name='school.issue.site',
        related='issue_type_id.site_id')
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
    education_level_id = fields.Many2one(
        comodel_name='education.level', string='Education Level')

    @api.model
    def default_get(self, var_fields):
        context = self.env.context
        res = super(WizCreateIssue, self).default_get(var_fields)
        student_id = context.get('active_id')
        group_id = context.get('education_group_id')
        group = self.env['education.group'].browse(
            group_id)
        schedule_id = context.get('education_schedule_id')
        schedule = self.env['education.schedule'].browse(schedule_id)
        school_id = context.get('school_id')
        level_id = group.level_id.id
        if not group_id and schedule:
            group = schedule.group_ids.filtered(
                lambda g: student_id in g.student_ids.ids)[:1]
            group_id = group.id
            level_id = group.level_id.id
        if not school_id:
            if schedule:
                school_id = schedule.center_id.id
            elif group:
                school_id = group.center_id.id
            elif student_id:
                student = self.env['res.partner'].browse(student_id)
                school_id = student.current_center_id.id
        res.update({
            'student_id': student_id,
            'education_schedule_id': schedule_id,
            'education_level_id': level_id,
            'group_id': group_id,
            'school_id': school_id,
        })
        return res

    @api.onchange('school_issue_type_id')
    def onchange_school_issue_type_id(self):
        for wizard in self:
            wizard.name = self.env['school.issue'].create_issue_name(
                wizard.student_id, wizard.school_issue_type_id,
                wizard.education_schedule_id)

    @api.multi
    def create_issue(self):
        self.ensure_one()
        if not self.school_issue_type_id:
            raise UserError(_('Please select an issue type!'))
        values = self.prepare_vals_for_create_issue()
        self.env['school.issue'].create(values)
        # Close wizard and reload view
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }

    def prepare_vals_for_create_issue(self):
        name = self.env['school.issue'].create_issue_name(
            self.student_id, self.school_issue_type_id,
            self.education_schedule_id)
        vals = {
            'name': name,
            'student_id': self.student_id.id,
            'school_id': self.school_id.id,
            'notes': self.notes or '',
            'school_issue_type_id': self.school_issue_type_id.id,
            'issue_type_id': self.issue_type_id.id,
            'requires_justification': self.requires_justification,
            'affect_to': self.affect_to,
            'reported_id': self.reported_id.id,
            'requires_imparting_group': self.requires_imparting_group,
            'issue_date': self.issue_date,
            'claim_id': self.claim_id.id,
            'site_id': self.site_id.id,
            'group_id': self.group_id.id,
            'proof_id': self.proof_id.id,
            'education_schedule_id': self.education_schedule_id.id,
        }
        return vals
