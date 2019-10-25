# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SchoolIssueSeverityScale(models.Model):
    _name = 'school.issue.severity.scale'
    _description = 'Issues severity scales'
    _order = 'gravity_scale DESC'

    name = fields.Char(string='Description', required=True, translate=True)
    gravity_scale = fields.Integer(
        string='Severity scale', default=0, required=True)

    @api.multi
    def unlink(self):
        scales = self.env.ref(
            'issue_education.school_issue_severity_scale_neutral')
        scales |= self.env.ref(
            'issue_education.school_issue_severity_scale_minor')
        scales |= self.env.ref(
            'issue_education.school_issue_severity_scale_inappropriate')
        scales |= self.env.ref(
            'issue_education.school_issue_severity_scale_no_coexistence')
        scales |= self.env.ref(
            'issue_education.school_issue_severity_scale_disruptive')
        scales |= self.env.ref(
            'issue_education.school_issue_severity_scale_positive')
        scales |= self.env.ref(
            'issue_education.school_issue_severity_scale_remarkable')
        if any(self.filtered(lambda s: s.id in scales.ids)):
            raise UserError(
                _('You cannot delete an issue scale created by the system.'))
        return super(SchoolIssueSeverityScale, self).unlink()
