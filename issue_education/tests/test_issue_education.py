# (c) 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import TransactionCase
from odoo.exceptions import Warning
from odoo import fields


class TestIssueEducation(TransactionCase):

    def setUp(self):
        super(TestIssueEducation, self).setUp()
        self.issue_obj = self.env['school.issue']
        self.issue_type_obj = self.env['school.issue.type']
        self.college_issue_type_obj = self.env['school.college.issue.type']
        self.site = self.env['school.issue.site'].create({
            'name': 'Site for test Issue education',
            'requires_imparting_group': True})
        vals = {'name': 'School issue type for test',
                'affect_to': 'student',
                'gravity_scale': '0'}
        self.issue_type = self.issue_type_obj.create(vals)

    def test_issue_education(self):
        issue_type_master = self.env.ref(
            "issue_education.schoolwork_issue_type_master")
        with self.assertRaises(Warning):
            issue_type_master.unlink()
        issue_site = self.env.ref(
            "issue_education.classroom_school_issue_site")
        with self.assertRaises(Warning):
            issue_site.unlink()
        res = dict(self.issue_type.name_get())[self.issue_type.id]
        self.assertEqual(res, 'School issue type for test   0(No evaluate)')
        vals = {'name': 'aa'}
        college_issue_type = self.college_issue_type_obj.create(vals)
        vals = {'issue_type_id': self.issue_type.id}
        college_issue_type.write(vals)
        college_issue_type.onchange_issue_type_id()
        self.assertEqual(college_issue_type.name,
                         'School issue type for test')
        self.issue_type.write({'requires_justification': True})
        vals = {
            'name': 'School issue for test',
            'issue_date': fields.Date.from_string(fields.Date.today()),
            'school_issue_type_id': college_issue_type.id,
            'site_id': self.site.id}
        issue = self.issue_obj.create(vals)
        issue.onchange_school_issue_type_id()
        self.assertEqual(issue.requires_justification, True)
        self.assertEqual(issue.issue_type_id.id,
                         college_issue_type.issue_type_id.id)
        self.assertEqual(issue.affect_to, 'student')
        issue.onchange_site_id()
        self.assertEqual(issue.requires_imparting_group, True)
