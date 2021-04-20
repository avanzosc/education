# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import TestIssueEducationKanbanCommon
from odoo.exceptions import UserError
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestIssueEducationKanbanView(TestIssueEducationKanbanCommon):

    def test_issue_from_group(self):
        action_dict = self.group.button_generate_view_issues()
        self.assertIn(
            ('id', 'in', self.group.student_ids.ids),
            action_dict.get('domain'))
        context = action_dict.get('context')
        self.assertEquals(context.get('education_group_id'), self.group.id)
        self.assertEquals(context.get('school_id'), self.group.center_id.id)

    def test_issue_from_schedule(self):
        action_dict = self.schedule.button_generate_view_issues()
        self.assertIn(
            ('id', 'in', self.schedule.student_ids.ids),
            action_dict.get('domain'))
        context = action_dict.get('context')
        self.assertEquals(
            context.get('education_schedule_id'), self.schedule.id)
        self.assertEquals(context.get('school_id'), self.schedule.center_id.id)

    def test_issue_education_kanban_group(self):
        context = {
            'active_id': self.student.id,
            'issue_type': self.college_issue_type.id,
            'education_group_id': self.group.id,
        }
        student_issues = self.student.with_context(context).student_issue_ids
        self.assertTrue(student_issues)
        student_issue = student_issues.filtered(
            lambda i: i.college_issue_type_id == self.college_issue_type)
        self.assertEquals(student_issue.issue_count, 0)
        self.assertEquals(student_issue.issues_on_day, 0)
        self.assertFalse(self.student.school_issue_ids)
        self.student.with_context(context).create_delete_issue()
        self.assertTrue(self.student.school_issue_ids)
        student_issue.invalidate_cache()
        self.assertEquals(student_issue.issue_count, 0)
        self.assertEquals(student_issue.issues_on_day, 1)
        self.student.with_context(context).create_delete_issue()
        self.assertFalse(self.student.school_issue_ids)
        student_issue.invalidate_cache()
        self.assertEquals(student_issue.issue_count, 0)
        self.assertEquals(student_issue.issues_on_day, 0)

    def test_issue_education_generic_kanban_group(self):
        context = {
            'active_id': self.student.id,
            'education_group_id': self.group.id,
        }
        student_issues = self.student.with_context(context).student_issue_ids
        self.assertTrue(student_issues)
        student_issue = student_issues.filtered(
            lambda i: i.college_issue_type_id == self.college_issue_type)
        self.assertEquals(student_issue.issue_count, 0)
        self.assertEquals(student_issue.issues_on_day, 0)
        wiz_model = self.wiz_create_model.with_context(context)
        wiz = wiz_model.create({
            'name': 'TEST',
            'school_issue_type_id': self.college_issue_type.id,
        })
        wiz.onchange_school_issue_type_id()
        self.assertEquals(wiz.name, self.issue_obj.create_issue_name(
            wiz.student_id, wiz.school_issue_type_id,
            wiz.education_schedule_id))
        self.assertFalse(wiz.education_schedule_id)
        self.assertEquals(wiz.student_id, self.student)
        self.assertEquals(wiz.group_id, self.group)
        self.assertEquals(wiz.school_id, self.edu_partner)
        wiz.create_issue()
        self.assertTrue(self.student.school_issue_ids)
        student_issue.invalidate_cache()
        self.assertEquals(student_issue.issue_count, 0)
        self.assertEquals(student_issue.issues_on_day, 1)

    def test_issue_education_kanban_schedule(self):
        context = {
            'active_id': self.student.id,
            'issue_type': self.college_issue_type.id,
            'education_schedule_id': self.schedule.id,
        }
        student_issues = self.student.with_context(context).student_issue_ids
        self.assertTrue(student_issues)
        self.student.with_context(context).create_delete_issue()
        self.assertTrue(self.student.school_issue_ids)
        school_issue = self.student.student_issue_ids.filtered(
            lambda i: i.college_issue_type_id == self.college_issue_type)
        self.assertEquals(school_issue.issue_count, 0)
        self.assertEquals(school_issue.issues_on_day, 1)
        self.student.with_context(context).create_delete_issue()
        self.assertFalse(self.student.school_issue_ids)
        school_issue.invalidate_cache()
        self.assertEquals(school_issue.issue_count, 0)
        self.assertEquals(school_issue.issues_on_day, 0)

    def test_issue_education_generic_kanban_schedule(self):
        context = {
            'active_id': self.student.id,
            'education_schedule_id': self.schedule.id,
        }
        self.issue_type.site_id = self.classroom
        student_issues = self.student.with_context(context).student_issue_ids
        self.assertTrue(student_issues)
        self.assertFalse(self.student.school_issue_ids)
        wiz_model = self.wiz_create_model.with_context(context)
        wiz = wiz_model.create({
            'name': 'TEST',
            'school_issue_type_id': self.college_issue_type.id,
        })
        wiz.onchange_school_issue_type_id()
        self.assertEquals(wiz.name, self.issue_obj.create_issue_name(
            wiz.student_id, wiz.school_issue_type_id,
            wiz.education_schedule_id))
        self.assertEquals(wiz.education_schedule_id, self.schedule)
        self.assertEquals(wiz.student_id, self.student)
        self.assertEquals(wiz.group_id, self.group)
        self.assertEquals(wiz.school_id, self.edu_partner)
        wiz.create_issue()
        self.assertTrue(self.student.school_issue_ids)
        school_issue = self.student.student_issue_ids.filtered(
            lambda i: i.college_issue_type_id == self.college_issue_type)
        self.assertEquals(school_issue.issue_count, 0)
        self.assertEquals(school_issue.issues_on_day, 1)

    def test_issue_education_generic_kanban_partner(self):
        context = {
            'active_id': self.student.id,
        }
        student_issues = self.student.with_context(context).student_issue_ids
        self.assertTrue(student_issues)
        student_issue = student_issues.filtered(
            lambda i: i.college_issue_type_id == self.college_issue_type)
        self.assertEquals(student_issue.issue_count, 0)
        self.assertEquals(student_issue.issues_on_day, 0)
        self.assertFalse(self.student.school_issue_ids)
        self.assertTrue(self.student.current_center_id)
        wiz_model = self.wiz_create_model.with_context(context)
        wiz = wiz_model.create({
            'name': 'TEST',
        })
        self.assertFalse(wiz.education_schedule_id)
        self.assertFalse(wiz.group_id)
        self.assertEquals(wiz.student_id, self.student)
        self.assertEquals(wiz.school_id, self.edu_partner)
        with self.assertRaises(UserError):
            wiz.create_issue()
        wiz.write({
            'school_issue_type_id': self.college_issue_type.id,
        })
        wiz.onchange_school_issue_type_id()
        self.assertEquals(wiz.name, self.issue_obj.create_issue_name(
            wiz.student_id, wiz.school_issue_type_id,
            wiz.education_schedule_id))
        wiz.create_issue()
        self.assertTrue(self.student.school_issue_ids)
        self.assertEquals(student_issue.issue_count, 0)
        self.assertEquals(student_issue.issues_on_day, 1)
