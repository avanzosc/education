# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.addons.resource_education.models.resource_calendar import \
    EDUCATION_DAYOFWEEK_CODE
from odoo.exceptions import ValidationError


class TestResourceEducation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResourceEducation, cls).setUpClass()
        start_hour = 10.0
        cls.hour_gap = 4.0
        cls.calendar = cls.env['resource.calendar'].create({
            'name': 'Test Hour Gap',
            'attendance_ids': [
                (0, 0, {'dayofweek': '1',
                        'name': 'Day1',
                        'hour_from': start_hour,
                        'hour_to': start_hour + cls.hour_gap}),
                (0, 0, {'dayofweek': '2',
                        'name': 'Day2',
                        'hour_from': start_hour,
                        'hour_to': start_hour + cls.hour_gap})]
        })

    def test_resource_calendar(self):
        for attendance in self.calendar.attendance_ids:
            self.assertEquals(
                attendance.dayofweek_education,
                EDUCATION_DAYOFWEEK_CODE.get(attendance.dayofweek))
            self.assertEquals(
                attendance.daily_hour, 1)

    def test_resource_calendar_code(self):
        with self.assertRaises(ValidationError):
            self.calendar.write({
                'education_code': '0000000',
            })
        with self.assertRaises(ValidationError):
            self.calendar.write({
                'education_code': '000000000',
            })
        self.calendar.write({
            'education_code': '00000000',
        })
