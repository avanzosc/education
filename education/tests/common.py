# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestEducationCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestEducationCommon, cls).setUpClass()
        cls.today = fields.Date.from_string(fields.Date.today())
        cls.academic_year_model = cls.env['education.academic_year']
        cls.evaluation_model = cls.env['education.academic_year.evaluation']
        cls.group_model = cls.env['education.group']
        cls.group_session_model = cls.env['education.group.session']
        cls.schedule_model = cls.env['education.schedule']
        cls.timetable_model = cls.env["education.schedule.timetable"]
        cls.subject_center_model = cls.env['education.subject.center']
        cls.attendance_model = cls.env['resource.calendar.attendance']
        cls.group_wizard = cls.env["education.group.next_year"].create({})
        cls.academic_year = cls.academic_year_model.search([
            ("current", "=", True)])
        if not cls.academic_year:
            start_year = cls.today.year
            if cls.today.month < 9:
                start_year -= 1
            cls.date_start = cls.today.replace(
                year=start_year, month=9, day=1)
            cls.date_end = cls.date_start.replace(
                year=cls.date_start.year + 1, month=8, day=31)
            cls.academic_year = cls.academic_year_model.create({
                'name': '{}+{}'.format(cls.date_start.year, cls.date_end.year),
                'date_start': cls.date_start,
                'date_end': cls.date_end,
            })
        cls.next_academic_year = cls.academic_year._get_next()
        if not cls.next_academic_year:
            next_date_start = cls.academic_year.date_start.replace(
                year=cls.academic_year.date_start.year + 1)
            next_date_end = cls.academic_year.date_start.replace(
                year=cls.academic_year.date_end.year + 1)
            cls.next_academic_year = cls.academic_year_model.create({
                'name': '{}+{}'.format(next_date_start.year,
                                       next_date_end.year),
                'date_start': next_date_start,
                'date_end': next_date_end,
            })
        cls.plan_model = cls.env['education.plan']
        cls.edu_plan_code = 'TEST'
        cls.edu_plan = cls.plan_model.create({
            'education_code': cls.edu_plan_code,
            'description': 'Test Plan',
        })
        cls.edu_level = cls.env['education.level'].create({
            'education_code': 'TEST',
            'description': 'Test Level',
            'plan_id': cls.edu_plan.id,
        })
        cls.edu_field = cls.env['education.field'].create({
            'education_code': 'TEST',
            'description': 'Test Field',
        })
        cls.edu_course = cls.env['education.course'].create({
            'education_code': 'TEST',
            'description': 'Test Course',
            'plan_id': cls.edu_plan.id,
            'level_id': cls.edu_level.id,
        })
        cls.edu_subject = cls.env['education.subject'].create({
            'education_code': 'TESTTEST',
            'description': 'Test Subject',
            'level_field_ids': [(0, 0, {
                'level_id': cls.edu_level.id,
                'field_id': cls.edu_field.id,
            })],
            'level_course_ids': [(0, 0, {
                'course_id': cls.edu_course.id,
                'level_id': cls.edu_level.id,
                'plan_id': cls.edu_plan.id,
            })],
        })
        cls.edu_partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
        cls.teacher = cls.env['hr.employee'].create({
            'name': 'Test Teacher',
            'user_id': cls.env.ref("base.user_admin").id,
        })
        cls.edu_classroom = cls.env['education.classroom'].create({
            'education_code': 'TEST',
            'description': 'Test Classroom',
            'center_id': cls.edu_partner.id,
        })
        cls.edu_task_type = cls.env['education.task_type'].create({
            'education_code': 'TEST',
            'description': 'Test Task Type',
            'type': 'L',
        })
        cls.edu_group_type = cls.env['education.group_type'].create({
            'education_code': 'TEST',
            'description': 'Test Group Type',
            'type': 'official',
        })
        cls.edu_lang = cls.env['education.language'].create({
            'education_code': '00',
            'description': 'Test Language',
        })
        cls.lang = cls.env['res.lang']._lang_get(cls.env.user.lang)
        cls.calendar = cls.env["resource.calendar"].create({
            "name": "Test Calendar",
            "attendance_ids": [(0, 0, {
                "name": "Monday from 9 to 10.30",
                "dayofweek": '0',
                "hour_from": 9.0,  # 09:00 AM
                "hour_to": 10.5,   # 10:30 AM
            })]
        })
