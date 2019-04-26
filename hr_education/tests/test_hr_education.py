# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.addons.education.tests.test_education import TestEducation


@common.at_install(False)
@common.post_install(True)
class TestHrEducation(TestEducation):

    @classmethod
    def setUpClass(cls):
        super(TestHrEducation, cls).setUpClass()
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
            })],
        })

    def test_education_academic_year(self):
        """Don't repeat this test."""
        pass

    def test_education_plan(self):
        """Don't repeat this test."""
        pass

    def test_education_subject(self):
        self.assertEquals(self.edu_subject.field_id, self.edu_field)
        self.assertEquals(self.edu_subject.level_id, self.edu_level)
        self.assertIn(self.edu_course, self.edu_subject.course_ids)
