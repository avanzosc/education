# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import TestContactsSchoolEducationCommon
from odoo.tests import common
from odoo.exceptions import UserError, ValidationError


@common.at_install(False)
@common.post_install(True)
class TestContactsSchoolEducation(TestContactsSchoolEducationCommon):

    def test_search(self):
        self.group.write({
            "student_ids": [(6, 0, self.student.ids)],
        })
        self.assertEquals(self.student.current_group_id, self.group)
        self.assertEquals(self.family, self.student.parent_id)
        self.assertEquals(self.family.children_number, 2)
        self.assertEquals(self.student.children_number, 2)
        students = self.partner_model.search([
            ('current_center_id', '=', self.edu_partner.id)])
        self.assertIn(self.student, students)
        students = self.partner_model.search([
            ('current_center_id', 'ilike', self.edu_partner.name)])
        self.assertIn(self.student, students)
        students = self.partner_model.search([
            ('current_course_id', '=', self.edu_course.id)])
        self.assertIn(self.student, students)
        students = self.partner_model.search([
            ('current_course_id', 'ilike', self.edu_course.description)])
        self.assertIn(self.student, students)
        parents = self.partner_model.search([
            ('childs_current_center_ids', '=', self.edu_partner.id)])
        self.assertIn(self.family, parents)
        parents = self.partner_model.search([
            ('childs_current_center_ids', 'ilike', self.edu_partner.name)])
        self.assertIn(self.family, parents)
        parents = self.partner_model.search([
            ('childs_current_course_ids', '=', self.edu_course.id)])
        self.assertIn(self.family, parents)
        self.assertIn(self.edu_partner, self.family.childs_current_center_ids)
        self.assertIn(self.edu_course, self.family.childs_current_course_ids)
        parents = self.partner_model.search([
            ('childs_current_course_ids', 'ilike',
             self.edu_course.description)])
        self.assertIn(self.family, parents)
        action_dict = self.family.button_open_current_student()
        self.assertFalse(action_dict)
        school_action_dict = self.edu_partner.button_open_current_student()
        self.assertIn(("current_center_id", "=", self.edu_partner.id),
                      school_action_dict.get("domain"))
        action_dict = self.edu_partner.button_open_relative_student()
        self.assertFalse(action_dict)
        family_action_dict = self.family.button_open_relative_student()
        students = self.family.mapped("family_ids.child2_id")
        self.assertIn(("student_id", "in", students.ids),
                      family_action_dict.get("domain"))
        self.student.educational_category = "otherchild"
        with self.assertRaises(UserError):
            self.student.get_current_group()
        self.assertEquals(self.family.children_number, 1)
        self.assertEquals(self.student.children_number, 1)

    def test_course_change(self):
        with self.assertRaises(ValidationError):
            self.change_model.create({
                'school_id': self.edu_partner.id,
                'next_school_id': self.edu_partner.id,
                'course_id': self.edu_course.id,
                'next_course_id': self.edu_course.id,
            })
        change_model = self.change_model.create({
            'school_id': self.edu_partner.id,
            'next_school_id': self.edu_partner.id,
            'course_id': self.edu_course2.id,
            'next_course_id': self.edu_course.id,
        })
        self.assertEquals(
            change_model.display_name, '{} ({}) - {} ({})'.format(
                change_model.course_id.description,
                change_model.school_id.display_name,
                change_model.next_course_id.description,
                change_model.next_school_id.display_name))
        self.assertIn(self.edu_subject, change_model.next_subject_ids)
        action_dict = change_model.button_open_subject_list()
        self.assertIn(("center_id", "=", change_model.next_school_id.id),
                      action_dict.get("domain"))
        self.assertIn(("course_id", "=", change_model.next_course_id.id),
                      action_dict.get("domain"))
        self.assertIn(("level_id", "=", change_model.next_level_id.id),
                      action_dict.get("domain"))
        context = action_dict.get("context")
        self.assertEquals(
            change_model.next_school_id.id, context.get("default_center_id"))
        self.assertEquals(
            change_model.next_course_id.id, context.get("default_course_id"))
        self.assertEquals(
            change_model.next_level_id.id, context.get("default_level_id"))
        with self.assertRaises(ValidationError):
            self.change_model.create({
                'school_id': self.edu_partner.id,
                'next_school_id': self.edu_partner.id,
                'course_id': self.edu_course2.id,
                'next_course_id': self.edu_course.id,
            })

    def test_create_group_schedule(self):
        group2 = self.group.copy(
            default={"academic_year_id": self.group.academic_year_id.id,
                     "education_code": "NXTGROUP"})
        self.assertFalse(group2.schedule_ids)
        group2.create_schedule()
        self.assertTrue(group2.schedule_ids)
        subject_center = self.subject_center_model.search([
            ("center_id", "=", group2.center_id.id),
            ("level_id", "=", group2.level_id.id),
            ("course_id", "=", group2.course_id.id),
        ])
        self.assertEquals(
            len(group2.schedule_ids), len(subject_center.mapped("subject_id")))

    def test_school_classroom(self):
        self.assertFalse(self.edu_partner2.classroom_ids)
        self.assertEquals(self.edu_partner2.classroom_count, 0)
        new_classroom = self.classroom_model.create({
            "center_id": self.edu_partner2.id,
            "education_code": "TEST",
            "description": "Test Classroom",
        })
        self.assertIn(new_classroom, self.edu_partner2.classroom_ids)
        self.assertEquals(self.edu_partner2.classroom_count, 1)
        classroom_dict = self.edu_partner2.button_open_classroom()
        self.assertIn(
            ("center_id", "in", self.edu_partner2.ids),
            classroom_dict.get('domain'))
        classroom_dict = self.student.button_open_classroom()
        self.assertFalse(classroom_dict)

    def test_create_schedule(self):
        self.group_wizard.create_next_year_groups()
        current_year = self.academic_year_model.search([
            ("current", "=", True)])
        next_year = current_year._get_next()
        self.assertTrue(next_year)
        next_groups = self.group_model.search([
            ("academic_year_id", "=", next_year.id),
            ("group_type_id.type", "=", "official")])
        self.assertTrue(next_groups)
        next_schedule = next_groups.mapped("schedule_ids")
        self.assertFalse(next_schedule)
        self.schedule_wizard.create_next_year_group_schedule()
        next_schedule = next_groups.mapped("schedule_ids")
        self.assertTrue(next_schedule)

    def test_assign_group(self):
        self.assertNotIn(self.group2, self.student.student_group_ids)
        self.assertNotEquals(self.student.current_group_id, self.group2)
        self.assertNotEquals(
            self.student.current_center_id, self.group2.center_id)
        self.assertNotEquals(
            self.student.current_level_id, self.group2.level_id)
        self.assertNotEquals(
            self.student.current_course_id, self.group2.course_id)
        self.student.assign_group(self.group2, update=True)
        self.assertIn(self.group2, self.student.student_group_ids)
        self.assertEquals(self.student.current_group_id, self.group2)
        self.assertEquals(
            self.student.current_center_id, self.group2.center_id)
        self.assertEquals(
            self.student.current_level_id, self.group2.level_id)
        self.assertEquals(
            self.student.current_course_id, self.group2.course_id)

    def test_permission_wizard(self):
        self.group.write({
            "student_ids": [(6, 0, self.student.ids)],
        })
        partners = self.student | self.family
        self.assertFalse(partners.mapped('permission_ids').filtered(
            lambda p: p.type_id == self.permission_type))
        wiz = self.permission_wiz_model.with_context(
            active_model=partners._name,
            active_ids=partners.ids).create({
                'type_id': self.permission_type.id,
            })
        self.assertNotEquals(wiz.student_ids, partners)
        self.assertEquals(wiz.student_ids, partners.filtered(
            lambda p: p.educational_category in ['student', 'otherchild']))
        wiz.create_permissions()
        self.assertTrue(partners.mapped('permission_ids').filtered(
            lambda p: p.type_id == self.permission_type))

    def test_partner_insurance_report_xlsx(self):
        report_name = (
            "contacts_school_education.partner_insurance_report_xlsx")
        with self.assertRaises(UserError):
            self.env.ref(report_name).render(self.student.ids)
        self.student.has_insurance = True  # needed to print on xlsx
        self.student.assign_group(self.group, update=True)
        self.assertEquals(
            self.student.current_center_id, self.edu_partner)
        report_xlsx = self.env.ref(report_name).render(self.edu_partner.ids)
        self.assertGreaterEqual(len(report_xlsx[0]), 1)
        self.assertEqual(report_xlsx[1], 'xlsx')
