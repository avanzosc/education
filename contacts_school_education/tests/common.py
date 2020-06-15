# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.education.tests.common import TestEducationCommon
from dateutil.relativedelta import relativedelta


class TestContactsSchoolEducationCommon(TestEducationCommon):

    @classmethod
    def setUpClass(cls):
        super(TestContactsSchoolEducationCommon, cls).setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.group_model = cls.env["education.group"]
        cls.classroom_model = cls.env["education.classroom"]
        cls.change_model = cls.env["education.course.change"]
        task_type_model = cls.env["education.task_type"]
        task_type = task_type_model.search([
            ("education_code", "=", "0120"),
        ])
        if not task_type:
            task_type.create({
                "education_code": "0120",
                "description": "TEST",
            })
        cls.language = cls.env["education.language"].create({
            "education_code": "TST_LANG",
            "description": "Test Language",
        })
        cls.edu_partner.educational_category = "school"
        cls.edu_partner2 = cls.edu_partner.copy()
        cls.edu_course.field_id = cls.edu_field
        cls.edu_course2 = cls.env["education.course"].create({
            "education_code": "CRS2",
            "description": "Test Course 2",
            "plan_id": cls.edu_plan.id,
            "level_id": cls.edu_level.id,
        })
        cls.student = cls.partner_model.create({
            "name": "Test Student",
            "educational_category": "student",
            "is_company": False,
        })
        cls.family = cls.partner_model.create({
            "name": "Test Family",
            "educational_category": "family",
            "is_company": True,
            "child_ids": [(6, 0, cls.student.ids)],
        })
        cls.academic_year.write({
            "date_start": cls.today - relativedelta(months=1),
            "date_end": cls.today + relativedelta(months=1),
        })
        cls.group_type = cls.env["education.group_type"].create({
            "education_code": "OFFI",
            "description": "Test Official",
            "type": "official",
        })
        cls.group = cls.group_model.create({
            "education_code": "GRPT",
            "description": "Test Group",
            "group_type_id": cls.group_type.id,
            "academic_year_id": cls.academic_year.id,
            "center_id": cls.edu_partner.id,
            "course_id": cls.edu_course.id,
            "level_id": cls.edu_level.id,
            "student_ids": [(6, 0, cls.student.ids)],
        })
        cls.schedule = cls.schedule_model.create({
            "center_id": cls.edu_partner.id,
            "academic_year_id": cls.academic_year.id,
            "teacher_id": cls.teacher.id,
            "task_type_id": cls.edu_task_type.id,
            "subject_id": cls.edu_subject.id,
            "group_ids": [(6, 0, cls.group.ids)],
        })
