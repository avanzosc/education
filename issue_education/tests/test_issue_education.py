# -*- coding: utf-8 -*-
# (c) 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import TransactionCase


class TestIssueEducation(TransactionCase):

    def setUp(self):
        super(TestIssueEducation, self).setUp()
        self.issue_type_obj = self.env['school.issue.type']
        self.college_issue_type_obj = self.env['school.college.issue.type']
        vals = {'name': 'School issue type for test'}
        self.issue_type = self.issue_type_obj.create(vals)

    def test_issue_education(self):
        vals = {'own_name': 'aa'}
        college_issue_type = self.college_issue_type_obj.create(vals)
        vals = {'issue_type_id': self.issue_type.id}
        college_issue_type.write(vals)
        college_issue_type.onchange_issue_type_id()
        self.assertEqual(college_issue_type.own_name,
                         'School issue type for test')
