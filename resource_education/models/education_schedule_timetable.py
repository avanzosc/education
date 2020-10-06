# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationScheduleTimetable(models.Model):
    _inherit = 'education.schedule.timetable'

    session_number = fields.Integer(
        related="attendance_id.daily_hour", store=True)
