# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

#    access_token = fields.Char('Access Token', groups="base.group_user")

    @api.multi
    def button_open_website_academic_records(self):
        self.ensure_one()
        url = '/schedule/%s/califications' % self.id
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }