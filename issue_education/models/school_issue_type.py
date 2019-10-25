# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, exceptions, fields, models


class SchoolIssueType(models.Model):
    _name = 'school.issue.type'
    _description = 'Types of issues'

    name = fields.Char(string='Description', required=True, translate=True)
    affect_to = fields.Selection(
        string='Affect to',
        selection=[('group', 'Group'),
                   ('student', 'Student')])
    gravity_scale_id = fields.Many2one(
        string='Severity scale', comodel_name='school.issue.severity.scale',
        required=True)
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
            result.append(
                (record.id,
                 '{}  ({})'.format(record.name, record.gravity_scale_id.name)))
        return result

    @api.multi
    def unlink(self):
        types = self.env.ref('issue_education.schoolwork_issue_type_master')
        types |= self.env.ref('issue_education.comes_late_issue_type_master')
        types |= self.env.ref('issue_education.assistance_issue_type_master')
        types |= self.env.ref('issue_education.uniformed_issue_type_master')
        types |= self.env.ref('issue_education.small_fault_issue_type_master')
        if any(self.filtered(lambda t: t.id in types.ids)):
            raise exceptions.UserError(
                _('You cannot delete an issue type created by the system.'))
        return super(SchoolIssueType, self).unlink()
