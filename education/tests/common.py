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
        cls.group_model = cls.env['education.group']
        cls.group_session_model = cls.env['education.group.session']
        cls.schedule_model = cls.env['education.schedule']
        cls.attendance_model = cls.env['resource.calendar.attendance']
        cls.academic_year = cls.academic_year_model.create({
            'name': '{}+{}'.format(cls.today.year + 10, cls.today.year + 11)
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
        cls.edu_course = cls.env['education.course'].create({
            'education_code': 'TEST',
            'description': 'Test Course',
            'plan_id': cls.edu_plan.id,
            'level_id': cls.edu_level.id,
        })
        cls.edu_field = cls.env['education.field'].create({
            'education_code': 'TEST',
            'description': 'Test Field',
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
