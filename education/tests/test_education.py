# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestEducation(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestEducation, cls).setUpClass()
        today = fields.Date.from_string(fields.Date.today())
        cls.academic_year = cls.env['education.academic_year'].create({
            'name': '{}+{}'.format(today.year + 10, today.year + 11)
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

    def test_education_academic_year(self):
        self.assertTrue(self.academic_year.active)
        self.academic_year.toggle_active()
        self.assertFalse(self.academic_year.active)

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
