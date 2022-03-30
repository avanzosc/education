# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

    @api.multi
    def button_open_website_academic_records(self):
        self.ensure_one()
        url = '/schedule/%s/califications' % self.id
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
