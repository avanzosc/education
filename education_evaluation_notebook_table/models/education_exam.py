# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class EducationExam(models.Model):
    _inherit = 'education.exam'

    @api.multi
    def button_open_website_academic_records(self):
        self.ensure_one()
        return self.schedule_id.button_open_website_academic_records()
