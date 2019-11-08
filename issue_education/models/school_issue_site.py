# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, exceptions, fields, models


class SchoolIssueSite(models.Model):
    _name = 'school.issue.site'
    _description = 'Issues sites'

    name = fields.Char(string='Description', required=True, translate=True)
    requires_imparting_group = fields.Boolean(
        string='Requires imparting group', default=False)

    @api.multi
    def unlink(self):
        sites = self.env.ref('issue_education.classroom_school_issue_site')
        if any(self.filtered(lambda s: s.id in sites.ids)):
            raise exceptions.UserError(
                _('You cannot delete an issue site created by the system.'))
        return super(SchoolIssueSite, self).unlink()
