# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationScheduleTimetable(models.Model):
    _inherit = "education.schedule.timetable"

    session_number = fields.Integer(
        compute="_compute_session_number", store=True)

    @api.depends("attendance_id", "attendance_id.daily_hour")
    def _compute_session_number(self):
        for record in self:
            record.session_number = record.attendance_id.daily_hour or 1
