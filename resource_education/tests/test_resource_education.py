# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.addons.education.tests.common import TestEducationCommon
from ..models.resource_calendar import EDUCATION_DAYOFWEEK_CODE
from odoo.exceptions import ValidationError


@common.at_install(False)
@common.post_install(True)
class TestResourceEducation(TestEducationCommon):
    @classmethod
    def setUpClass(cls):
        super(TestResourceEducation, cls).setUpClass()
        start_hour = 10.0
        cls.hour_gap = 4.0
        cls.calendar = cls.env["resource.calendar"].create({
            "name": "Test Hour Gap",
            "attendance_ids": [
                (0, 0, {"dayofweek": "1",
                        "name": "Day1",
                        "hour_from": start_hour,
                        "hour_to": start_hour + cls.hour_gap}),
                (0, 0, {"dayofweek": "2",
                        "name": "Day2",
                        "hour_from": start_hour,
                        "hour_to": start_hour + cls.hour_gap})]
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
                "education_code": "0000000",
            })
        with self.assertRaises(ValidationError):
            self.calendar.write({
                "education_code": "000000000",
            })
        self.calendar.write({
            "education_code": "00000000",
        })

    def test_schedule_timetable(self):
        group = self.group_model.create({
            "education_code": "TEST",
            "description": "Test Group",
            "center_id": self.edu_partner.id,
            "academic_year_id": self.academic_year.id,
            "level_id": self.edu_level.id,
            "student_ids": [(6, 0, self.edu_partner.ids)],
            "group_type_id": self.edu_group_type.id,
            "calendar_id": self.calendar.id,
            "plan_id": self.edu_plan.id,
        })
        schedule = self.schedule_model.create({
            "center_id": self.edu_partner.id,
            "academic_year_id": self.academic_year.id,
            "teacher_id": self.teacher.id,
            "task_type_id": self.edu_task_type.id,
            "subject_id": self.edu_subject.id,
            "group_ids": [(6, 0, group.ids)],
        })
        self.assertEquals(schedule.calendar_id, self.calendar)
        attendance = schedule.calendar_id.attendance_ids[:1]
        timetable = self.timetable_model.new({
            "schedule_id": schedule.id,
            "calendar_id": schedule.calendar_id.id,
            "dayofweek": attendance.dayofweek,
            "attendance_id": attendance.id,
        })
        self.assertEquals(timetable.session_number, attendance.daily_hour)
