# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import TestContactsSchoolEducationCommon
from odoo.tests import common
from odoo.exceptions import ValidationError


@common.at_install(False)
@common.post_install(True)
class TestContactsSchoolEducation(TestContactsSchoolEducationCommon):

    def test_search(self):
        self.student.update_current_group_id()
        self.assertEquals(self.student.current_group_id, self.group)
        self.assertEquals(self.family, self.student.parent_id)
        students = self.partner_model.search([
            ('current_center_id', '=', self.school.id)])
        self.assertIn(self.student, students)
        students = self.partner_model.search([
            ('current_center_id', 'ilike', self.school.name)])
        self.assertIn(self.student, students)
        students = self.partner_model.search([
            ('current_course_id', '=', self.edu_course.id)])
        self.assertIn(self.student, students)
        students = self.partner_model.search([
            ('current_course_id', 'ilike', self.edu_course.description)])
        self.assertIn(self.student, students)
        parents = self.partner_model.search([
            ('childs_current_center_ids', '=', self.school.id)])
        self.assertIn(self.family, parents)
        parents = self.partner_model.search([
            ('childs_current_center_ids', 'ilike', self.school.name)])
        self.assertIn(self.family, parents)
        parents = self.partner_model.search([
            ('childs_current_course_ids', '=', self.edu_course.id)])
        self.assertIn(self.family, parents)
        self.assertIn(self.school, self.family.childs_current_center_ids)
        self.assertIn(self.edu_course, self.family.childs_current_course_ids)
        parents = self.partner_model.search([
            ('childs_current_course_ids', 'ilike',
             self.edu_course.description)])
        self.assertIn(self.family, parents)
        action_dict = self.family.button_open_current_student()
        self.assertFalse(action_dict)
        school_action_dict = self.school.button_open_current_student()
        self.assertIn(("current_center_id", "=", self.school.id),
                      school_action_dict.get("domain"))
        action_dict = self.school.button_open_relative_student()
        self.assertFalse(action_dict)
        family_action_dict = self.family.button_open_relative_student()
        students = self.family.mapped("family_ids.child2_id")
        self.assertIn(("student_id", "in", students.ids),
                      family_action_dict.get("domain"))

    def test_course_change(self):
        with self.assertRaises(ValidationError):
            self.change_model.create({
                'school_id': self.school.id,
                'next_school_id': self.school.id,
                'course_id': self.edu_course.id,
                'next_course_id': self.edu_course.id,
            })
        change_model = self.change_model.create({
            'school_id': self.school.id,
            'next_school_id': self.school.id,
            'course_id': self.edu_course2.id,
            'next_course_id': self.edu_course.id,
        })
        self.assertEquals(
            change_model.display_name, '{} ({}) - {} ({})'.format(
                change_model.course_id.description,
                change_model.school_id.display_name,
                change_model.next_course_id.description,
                change_model.next_school_id.display_name))
        self.assertFalse(change_model.next_subject_ids)
        change_model.button_add_subject_list()
        self.assertIn(self.edu_subject, change_model.next_subject_ids)
        with self.assertRaises(ValidationError):
            self.change_model.create({
                'school_id': self.school.id,
                'next_school_id': self.school.id,
                'course_id': self.edu_course2.id,
                'next_course_id': self.edu_course.id,
            })

    def test_school_classroom(self):
        self.assertFalse(self.school.classroom_ids)
        self.assertEquals(self.school.classroom_count, 0)
        new_classroom = self.classroom_model.create({
            "center_id": self.school.id,
            "education_code": "TEST",
            "description": "Test Classroom",
        })
        self.assertIn(new_classroom, self.school.classroom_ids)
        self.assertEquals(self.school.classroom_count, 1)
        classroom_dict = self.school.button_open_classroom()
        self.assertIn(
            ("center_id", "in", self.school.ids), classroom_dict.get('domain'))
