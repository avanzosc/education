# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError
from odoo.addons.education.tests.test_education import TestEducation


@common.at_install(False)
@common.post_install(True)
class TestContactsSchoolEducation(TestEducation):

    @classmethod
    def setUpClass(cls):
        super(TestContactsSchoolEducation, cls).setUpClass()
        cls.change_model = cls.env['education.course.change']
        cls.school = cls.env['res.partner'].create({
            'name': 'School Test',
            'educational_category': 'school',
        })
        cls.edu_course2 = cls.env['education.course'].create({
            'education_code': 'TES2',
            'description': 'Test Course 2',
            'plan_id': cls.edu_plan.id,
            'level_id': cls.edu_level.id,
        })

    def test_course_change(self):
        with self.assertRaises(ValidationError):
            self.change_model.create({
                'school_id': self.school.id,
                'next_school_id': self.school.id,
                'course_id': self.edu_course.id,
                'next_course_id': self.edu_course.id,
            })
        self.change_model.create({
            'school_id': self.school.id,
            'next_school_id': self.school.id,
            'course_id': self.edu_course.id,
            'next_course_id': self.edu_course2.id,
        })

    def test_education_academic_year(self):
        """Don't repeat this test."""
        pass

    def test_education_plan(self):
        """Don't repeat this test."""
        pass

    def test_education_level_course_subject(self):
        """Don't repeat this test."""
        pass

    def test_education_subject(self):
        """Don't repeat this test."""
        pass

    def test_education_level(self):
        """Don't repeat this test."""
        pass
