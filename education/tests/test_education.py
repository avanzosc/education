# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common
from odoo.exceptions import ValidationError


@common.at_install(False)
@common.post_install(True)
class TestEducation(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestEducation, cls).setUpClass()
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

    def test_education_academic_year(self):
        self.assertTrue(self.academic_year.active)
        self.academic_year.toggle_active()
        self.assertFalse(self.academic_year.active)
        with self.assertRaises(ValidationError):
            self.academic_year_model.create({
                'name': 'TEST',
            })
        with self.assertRaises(ValidationError):
            self.academic_year.write({
                'date_start': self.today,
                'date_end': self.today,
            })

    def test_education_plan(self):
        self.assertTrue(self.edu_plan.active)
        self.assertTrue(self.edu_level.active)
        self.assertTrue(self.edu_course.active)
        self.assertEquals(
            self.edu_plan.display_name,
            '[{}] {}'.format(self.edu_plan.education_code,
                             self.edu_plan.description))
        search_plans = self.plan_model.name_search(name=self.edu_plan_code)
        self.assertIn(self.edu_plan.id,
                      set(plan_id[0] for plan_id in search_plans))
        self.edu_plan.toggle_active()
        self.assertFalse(self.edu_plan.active)
        self.assertFalse(self.edu_level.active)
        self.assertFalse(self.edu_course.active)

    def test_education_level_course_subject(self):
        relation = self.edu_subject.level_course_ids[:1]
        self.assertEquals(
            relation.display_name,
            '{}{}{}{}'.format(
                relation.level_id.education_code,
                relation.plan_id.education_code,
                relation.course_id.education_code,
                relation.subject_id.education_code))

    def test_education_subject(self):
        self.assertIn(self.edu_level, self.edu_subject.level_ids)
        self.assertIn(self.edu_course, self.edu_subject.course_ids)
        self.assertIn(self.edu_field, self.edu_subject.field_ids)

    def test_education_level(self):
        self.assertEquals(
            self.edu_level.display_name,
            '[{}] {} ({})'.format(
                self.edu_level.education_code, self.edu_level.description,
                self.edu_level.plan_id.description))

    def test_education_classroom(self):
        self.assertEquals(
            self.edu_classroom.display_name,
            '[{}] {} ({})'.format(
                self.edu_classroom.education_code,
                self.edu_classroom.description,
                self.edu_classroom.center_id.name))

    def test_education_group_session_default(self):
        session_dict = self.group_session_model.default_get(['dayofweek'])
        attendance_dict = self.attendance_model.default_get(['dayofweek'])
        self.assertEquals(
            session_dict.get('dayofweek'), attendance_dict.get('dayofweek'))

    def test_education_schedule_default(self):
        schedule_dict = self.schedule_model.default_get(['dayofweek'])
        attendance_dict = self.attendance_model.default_get(['dayofweek'])
        self.assertEquals(
            schedule_dict.get('dayofweek'), attendance_dict.get('dayofweek'))

    def test_education_group(self):
        group = self.group_model.create({
            'education_code': 'TEST',
            'description': 'Test Group',
            'center_id': self.edu_partner.id,
            'academic_year_id': self.academic_year.id,
            'level_id': self.edu_level.id,
            'student_ids': [(6, 0, self.edu_partner.ids)],
        })
        self.assertEquals(group.student_count, len(group.student_ids))
        with self.assertRaises(ValidationError):
            group.write({
                'parent_id': group.id,
            })
        self.assertEquals(self.edu_partner.education_group_count, 1)
        action_dict = self.edu_partner.button_open_education_groups()
        self.assertEquals(action_dict.get('domain'),
                          [('center_id', '=', self.edu_partner.id)])
        action_dict = group.button_open_students()
        self.assertEquals(action_dict.get('domain'),
                          [('id', 'in', group.student_ids.ids)])
        schedule = self.schedule_model.create({
            'center_id': self.edu_partner.id,
            'academic_year_id': self.academic_year.id,
            'teacher_id': self.teacher.id,
            'task_type_id': self.edu_task_type.id,
            'subject_id': self.edu_subject.id,
            'group_ids': [(6, 0, group.ids)],
            'hour_from': 12.0,
            'hour_to': 13.0,
        })
        self.assertEquals(schedule.student_ids, group.student_ids)
        self.assertEquals(group.schedule_count, len(group.schedule_ids))
        action_dict = group.button_open_schedule()
        self.assertEquals(action_dict.get('domain'),
                          [('id', 'in', group.schedule_ids.ids)])
        self.assertEquals(
            schedule.display_name,
            '{} [{}]'.format(self.edu_subject.description,
                             self.teacher.name))
        self.assertEquals(schedule.task_type_type, self.edu_task_type.type)
