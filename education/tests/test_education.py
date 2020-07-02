# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import TestEducationCommon
from odoo import _
from odoo.tests import common
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


@common.at_install(False)
@common.post_install(True)
class TestEducation(TestEducationCommon):

    def test_education_lang(self):
        self.edu_lang.write({
            'lang_id': self.lang.id,
        })
        self.assertEquals(self.env.user.lang, self.edu_lang.lang_id.code)
        self.assertEquals(self.lang.edu_lang_id, self.edu_lang)

    def test_education_academic_year(self):
        self.assertTrue(self.academic_year.active)
        with self.assertRaises(ValidationError):
            self.academic_year_model.create({
                'name': 'TEST',
            })
        self.evaluation_model.create({
            'name': 'Evaluation',
            'academic_year_id': self.academic_year.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
        })
        with self.assertRaises(ValidationError):
            self.academic_year.write({
                'date_start': self.today,
                'date_end': self.today,
            })
        with self.assertRaises(ValidationError):
            self.academic_year.write({
                'date_start': self.date_start + relativedelta(days=1),
                'date_end': self.date_end,
            })
        with self.assertRaises(ValidationError):
            self.academic_year.write({
                'date_start': self.date_start,
                'date_end': self.date_end - relativedelta(days=1),
            })
        self.academic_year.toggle_active()
        self.assertFalse(self.academic_year.active)

    def test_education_academic_year_current(self):
        date_start = self.today - relativedelta(months=1)
        self.academic_year.write({
            'date_start': date_start,
            'date_end': date_start + relativedelta(months=2),
        })
        self.assertTrue(self.academic_year.current)
        self.assertIn(
            self.academic_year, self.academic_year_model.search([
                ('current', '=', True)]))
        date_start = self.today + relativedelta(months=1)
        self.academic_year.write({
            'date_start': date_start,
            'date_end': date_start + relativedelta(months=2),
        })
        self.academic_year.invalidate_cache()
        self.assertFalse(self.academic_year.current)
        self.assertIn(
            self.academic_year, self.academic_year_model.search([
                ('current', '!=', True)]))

    def test_education_academic_year_evaluation(self):
        with self.assertRaises(ValidationError):
            self.evaluation_model.create({
                'name': 'Start > End',
                'academic_year_id': self.academic_year.id,
                'date_start': self.date_end,
                'date_end': self.date_start,
            })
        with self.assertRaises(ValidationError):
            self.evaluation_model.create({
                'name': 'Evaluation before Year',
                'academic_year_id': self.academic_year.id,
                'date_start': self.date_start - relativedelta(months=1),
                'date_end': self.date_start - relativedelta(days=1),
            })
        with self.assertRaises(ValidationError):
            self.evaluation_model.create({
                'name': 'Evaluation after Year',
                'academic_year_id': self.academic_year.id,
                'date_start': self.date_end + relativedelta(days=1),
                'date_end': self.date_end + relativedelta(months=1),
            })
        with self.assertRaises(ValidationError):
            self.evaluation_model.create({
                'name': 'Evaluation Start < Year Start',
                'academic_year_id': self.academic_year.id,
                'date_start': self.date_start - relativedelta(days=1),
                'date_end': self.date_end,
            })
        with self.assertRaises(ValidationError):
            self.evaluation_model.create({
                'name': 'Evaluation End > Year End',
                'academic_year_id': self.academic_year.id,
                'date_start': self.date_start,
                'date_end': self.date_end + relativedelta(days=1),
            })
        with self.assertRaises(ValidationError):
            self.evaluation_model.create({
                'name': 'Evaluation longer Year',
                'academic_year_id': self.academic_year.id,
                'date_start': self.date_start - relativedelta(months=1),
                'date_end': self.date_end + relativedelta(months=1),
            })
        evaluation = self.evaluation_model.create({
            'name': 'Full Year Evaluation',
            'academic_year_id': self.academic_year.id,
            'date_start': self.academic_year.date_start,
            'date_end': self.academic_year.date_end,
        })
        new_evaluation = evaluation.copy()
        self.assertEquals(
            _('{} (copy)').format(evaluation.name), new_evaluation.name)

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
        self.assertIn(self.edu_course, self.edu_subject.course_ids)
        self.assertEquals(
            self.edu_subject.mapped('level_course_ids.course_id'),
            self.edu_subject.course_ids)
        self.assertEquals(
            self.edu_subject.mapped('level_field_ids.field_id'),
            self.edu_subject.field_ids)
        self.assertIn(self.edu_field, self.edu_subject.field_ids)
        self.assertIn(self.edu_level, self.edu_subject.level_ids)
        self.assertEquals(
            (self.edu_subject.mapped('level_course_ids.level_id') |
             self.edu_subject.mapped('level_field_ids.level_id')),
            self.edu_subject.level_ids)
        action_dict = self.edu_subject.button_open_subject_center()
        self.assertEquals(action_dict.get('domain'),
                          [('subject_id', '=', self.edu_subject.id)])

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

    def test_education_course(self):
        self.assertEquals(
            self.edu_course.display_name,
            '[{}] {}'.format(
                self.edu_course.education_code,
                self.edu_course.description))
        self.edu_course.field_id = self.edu_field
        self.edu_course.invalidate_cache()
        self.assertEquals(
            self.edu_course.display_name,
            '[{}] {} ({})'.format(
                self.edu_course.education_code,
                self.edu_course.description,
                self.edu_field.description))

    def test_education_group_session_default(self):
        session_dict = self.group_session_model.default_get(['dayofweek'])
        attendance_dict = self.attendance_model.default_get(['dayofweek'])
        self.assertEquals(
            session_dict.get('dayofweek'), attendance_dict.get('dayofweek'))

    def test_education_group(self):
        group = self.group_model.create({
            'education_code': 'TEST',
            'description': 'Test Group',
            'center_id': self.edu_partner.id,
            'academic_year_id': self.academic_year.id,
            'level_id': self.edu_level.id,
            'student_ids': [(6, 0, self.edu_partner.ids)],
            'group_type_id': self.edu_group_type.id,
        })
        self.assertEquals(group.student_count, len(group.student_ids))
        with self.assertRaises(ValidationError):
            group.write({
                'parent_id': group.id,
            })
        self.assertEquals(self.edu_partner.education_group_count, 1)
        action_dict = self.edu_partner.button_open_education_groups()
        self.assertIn(
            ('center_id', '=', self.edu_partner.id), action_dict.get('domain'))
        action_dict = group.button_open_students()
        self.assertIn(
            ('id', 'in', group.student_ids.ids), action_dict.get('domain'))
        schedule = self.schedule_model.create({
            'center_id': self.edu_partner.id,
            'academic_year_id': self.academic_year.id,
            'teacher_id': self.teacher.id,
            'task_type_id': self.edu_task_type.id,
            'subject_id': self.edu_subject.id,
            'group_ids': [(6, 0, group.ids)],
        })
        action_dict = self.teacher.button_open_schedule()
        self.assertIn(("professor_id", "=", self.teacher.id),
                      action_dict.get('domain'))
        self.assertEquals(schedule.student_ids, group.student_ids)
        self.assertEquals(group.schedule_count, len(group.schedule_ids))
        action_dict = group.button_open_schedule()
        self.assertIn(
            ('id', 'in', group.schedule_ids.ids), action_dict.get('domain'))
        action_dict = group.button_edit_students()
        self.assertIn(
            ('id', 'in', group.student_ids.ids), action_dict.get('domain'))
        action_dict = schedule.button_open_students()
        self.assertIn(('id', 'in', schedule.mapped('student_ids').ids),
                      action_dict.get('domain'))
        self.assertEquals(
            schedule.display_name,
            '{} [{}]'.format(self.edu_subject.description,
                             self.teacher.name))
        self.assertEquals(schedule.task_type_type, self.edu_task_type.type)
        self.assertTrue(group.academic_year_id._get_next())
        group.create_next_academic_year()
        next_group = self.group_model.search([
            ('education_code', '=', group.education_code),
            ('academic_year_id', '=', group.academic_year_id._get_next().id)
        ])
        self.assertTrue(next_group)

    def test_education_next_year_group(self):
        self.assertEquals(self.edu_group_type.type, "official")
        self.group_model.create({
            'education_code': 'TEST',
            'description': 'Test Group',
            'center_id': self.edu_partner.id,
            'academic_year_id': self.academic_year.id,
            'level_id': self.edu_level.id,
            'student_ids': [(6, 0, self.edu_partner.ids)],
            'group_type_id': self.edu_group_type.id,
        })
        current_year = self.academic_year_model.search([
            ("current", "=", True)])
        current_groups = self.group_model.search([
            ("academic_year_id.current", "=", True),
            ("group_type_id.type", "=", "official")])
        next_year = current_year._get_next()
        next_groups = self.group_model.search([
            ("academic_year_id", "=", next_year.id),
            ("group_type_id.type", "=", "official")])
        self.assertTrue(current_groups)
        self.assertFalse(next_groups)
        self.group_wizard.create_next_year_groups()
        next_groups = self.group_model.search([
            ("academic_year_id", "=", next_year.id),
            ("group_type_id.type", "=", "official")])
        self.assertTrue(next_groups)
        self.assertEquals(len(current_groups), len(next_groups))

    def test_education_group_student_edit(self):
        group = self.group_model.create({
            'education_code': 'TEST',
            'description': 'Test Group',
            'center_id': self.edu_partner.id,
            'academic_year_id': self.academic_year.id,
            'level_id': self.edu_level.id,
            'student_ids': [(6, 0, self.edu_partner.ids)],
        })
        with self.assertRaises(UserError):
            group.button_edit_students()
