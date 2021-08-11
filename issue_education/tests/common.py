# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields
from odoo.addons.education.tests.common import TestEducationCommon


class TestIssueEducationCommon(TestEducationCommon):

    @classmethod
    def setUpClass(cls):
        super(TestIssueEducationCommon, cls).setUpClass()
        cls.partner_obj = cls.env['res.partner']
        cls.issue_obj = cls.env['school.issue']
        cls.issue_type_obj = cls.env['school.issue.type']
        cls.college_issue_type_obj = cls.env['school.college.issue.type']
        cls.proof_obj = cls.env['school.issue.proof']
        cls.measure_obj = cls.env['school.college.educational.measure']
        cls.scale_obj = cls.env['school.issue.severity.scale']
        cls.site_obj = cls.env['school.issue.site']
        cls.edu_partner.write({
            'educational_category': 'school',
        })
        cls.family = cls.partner_obj.create({
            'name': 'Family',
            'educational_category': 'family',
        })
        cls.progenitor = cls.partner_obj.create({
            'name': 'Parent',
            'educational_category': 'progenitor',
        })
        cls.student = cls.partner_obj.create({
            'name': 'Student',
            'educational_category': 'student',
            'child2_ids': [(0, 0, {
                'responsible_id': cls.progenitor.id,
                'family_id': cls.family.id,
            })],
        })
        cls.group = cls.group_model.create({
            'education_code': 'TEST',
            'description': 'Test Group',
            'center_id': cls.edu_partner.id,
            'academic_year_id': cls.academic_year.id,
            'plan_id': cls.edu_plan.id,
            'level_id': cls.edu_level.id,
            'course_id': cls.edu_course.id,
            'group_type_id': cls.edu_group_type.id,
            'student_ids': [(6, 0, cls.student.ids)],
        })
        cls.schedule = cls.schedule_model.create({
            'center_id': cls.edu_partner.id,
            'academic_year_id': cls.academic_year.id,
            'teacher_id': cls.teacher.id,
            'task_type_id': cls.edu_task_type.id,
            'subject_id': cls.edu_subject.id,
            'group_ids': [(6, 0, cls.group.ids)],
        })
        cls.site = cls.env['school.issue.site'].create({
            'name': 'Site for test Issue education',
            'requires_imparting_group': True,
        })
        cls.issue_type = cls.issue_type_obj.create({
            'name': 'School issue type for test',
            'affect_to': 'student',
            'gravity_scale_id': cls.env.ref(
                'issue_education.school_issue_severity_scale_minor').id,
            'generate_part': True,
        })
        cls.measure = cls.measure_obj.create({
            'name': 'Test Measure',
            'school_id': cls.edu_partner.id,
            'severity_level_id': cls.env.ref(
                'issue_education.school_issue_severity_scale_neutral').id,
        })
        cls.college_issue_type = cls.college_issue_type_obj.create({
            'name': cls.issue_type.name,
            'issue_type_id': cls.issue_type.id,
            'school_id': cls.edu_partner.id,
            'notify_ids': [(6, 0, cls.progenitor.ids)],
            'educational_measure_ids': [(6, 0, cls.measure.ids)],
        })
        cls.proof = cls.proof_obj.create({
            'name': 'Test Proof',
            'person_id': cls.progenitor.id,
            'student_id': cls.student.id,
        })
        cls.issue_vals = {
            'name': 'School issue for test',
            'student_id': cls.student.id,
            'issue_date': fields.Date.today(),
            'school_issue_type_id': cls.college_issue_type.id,
            'school_id': cls.college_issue_type.school_id.id,
            'site_id': cls.site.id,
            'reported_id': cls.env.user.id,
            'education_schedule_id': cls.schedule.id,
        }
