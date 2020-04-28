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
        cls.school = cls.env["res.partner"].create({
            "name": "School Test",
            "educational_category": "school",
        })
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
            "center_id": cls.school.id,
            "course_id": cls.edu_course.id,
            "level_id": cls.edu_level.id,
            "student_ids": [(6, 0, cls.student.ids)],
        })
