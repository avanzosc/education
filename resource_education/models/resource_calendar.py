# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

EDUCATION_DAYOFWEEK_CODE = {
    '0': 1,  # Monday
    '1': 2,  # Tuesday
    '2': 3,  # Wednesday
    '3': 4,  # Thursday
    '4': 5,  # Friday
    '5': 6,  # Saturday
    '6': 7,  # Sunday
}


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    education_code = fields.Char(
        string='Education Code', copy=False)

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 8
        for record in self.filtered('education_code'):
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))


class ResourceCalendarLine(models.Model):
    _inherit = 'resource.calendar.attendance'

    dayofweek_education = fields.Integer(
        string='Education Day of Week Code',
        compute='_compute_dayofweek_education', store=True)
    daily_hour = fields.Integer(
        string='Hour in Day', compute='_compute_daily_hour')

    @api.model
    def default_get(self, fields_list):
        res = super(ResourceCalendarLine, self).default_get(fields_list)
        return res

    @api.depends('dayofweek')
    def _compute_dayofweek_education(self):
        for record in self:
            record.dayofweek_education = (
                EDUCATION_DAYOFWEEK_CODE.get(record.dayofweek))

    @api.depends('hour_from', 'calendar_id', 'calendar_id.attendance_ids',
                 'calendar_id.attendance_ids.hour_from')
    def _compute_daily_hour(self):
        for calendar in self.mapped('calendar_id'):
            daily_hour = 1
            for line in calendar.attendance_ids:
                line.daily_hour = daily_hour
                daily_hour += 1
