# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from .common import TestIssueEducationCommon
from odoo.tests import common
from odoo.exceptions import UserError
from odoo import fields


@common.at_install(False)
@common.post_install(True)
class TestIssueEducation(TestIssueEducationCommon):

    def test_affect_to(self):
        issue_type_sel = self.env['school.issue.type'].fields_get(
            allfields=['affect_to'])['affect_to']['selection']
        school_issue_type_sel = self.env[
            'school.college.issue.type']._get_selection_affect_to()
        self.assertEquals(issue_type_sel, school_issue_type_sel)

    def test_system_issue_type_erase(self):
        scale_neutral = self.env.ref(
            "issue_education.school_issue_severity_scale_neutral")
        issue_type = self.issue_type_obj.create({
            'name': 'Test Type',
            'gravity_scale_id': scale_neutral.id,
        })
        issue_type_master = self.env.ref(
            "issue_education.schoolwork_issue_type_master")
        with self.assertRaises(UserError):
            issue_type_master.unlink()
        issue_type.unlink()

    def test_system_issue_site_erase(self):
        site = self.site_obj.create({
            'name': 'Test Site',
        })
        issue_site = self.env.ref(
            "issue_education.classroom_school_issue_site")
        with self.assertRaises(UserError):
            issue_site.unlink()
        site.unlink()

    def test_system_issue_scale_erase(self):
        scale = self.scale_obj.create({
            'name': 'Test Scale',
        })
        scale_minor = self.env.ref(
            "issue_education.school_issue_severity_scale_minor")
        with self.assertRaises(UserError):
            scale_minor.unlink()
        scale.unlink()

    def test_college_issue(self):
        self.assertEquals(
            self.issue_type.display_name,
            '{}  ({})'.format(self.issue_type.name,
                              self.issue_type.gravity_scale_id.name))
        vals = {
            'name': 'aa',
            'issue_type_id': self.issue_type.id,
            'school_id': self.edu_partner.id,
        }
        college_issue_type = self.college_issue_type_obj.create(vals)
        college_issue_type.onchange_issue_type_id()

        self.assertEquals(
            college_issue_type.display_name,
            '{}  ({})'.format(college_issue_type.name,
                              college_issue_type.gravity_scale_id.name))
        self.assertEquals(
            college_issue_type.name,
            'School issue type for test')

    def test_issue_education(self):
        vals = {
            'name': 'School issue for test',
            'student_id': self.student.id,
            'issue_date': fields.Date.today(),
            'school_issue_type_id': self.college_issue_type.id,
            'school_id': self.college_issue_type.school_id.id,
            'site_id': self.site.id,
            'reported_id': self.env.user.id,
        }
        issue = self.issue_obj.create(vals)
        self.assertTrue(issue.claim_id)
        self.assertEquals(issue.proof_state, 'optional')
        self.assertIn(self.progenitor, issue.claim_id.message_partner_ids)
        self.assertIn(self.measure, issue.claim_id.educational_measure_ids)
        issue.issue_type_id.requires_justification = True
        issue.onchange_school_issue_type_id()
        self.assertEquals(issue.requires_justification, True)
        self.assertEquals(issue.proof_state, 'required')
        self.assertEquals(issue.issue_type_id.id,
                          self.college_issue_type.issue_type_id.id)
        self.assertEquals(issue.affect_to, 'student')
        issue.proof_id = self.proof
        self.assertEquals(issue.proof_state, 'proved')
        issue.onchange_site_id()
        self.assertEquals(issue.requires_imparting_group, True)
        self.assertFalse(issue.claim_id.calendar_event_count)
        issue.claim_id.button_notified()
        issue.claim_id.invalidate_cache()
        self.assertEquals(issue.claim_id.state, 'notified')
        self.assertEquals(issue.claim_id.calendar_event_count, 1)
        issue.claim_id.button_confirmed()
        self.assertEquals(issue.claim_id.state, 'confirmed')
        issue.claim_id.button_fulfill()
        self.assertEquals(issue.claim_id.state, 'fulfill')
        issue.claim_id.button_closed()
        self.assertEquals(issue.claim_id.state, 'closed')
        action_dict = issue.claim_id.open_calendar_event()
        self.assertIn(
            ('res_id', '=', issue.claim_id.id), action_dict.get('domain'))
        action_dict = self.student.button_open_school_issues()
        self.assertIn(
            ('student_id', 'in', self.student.ids), action_dict.get('domain'))
        self.assertEquals(action_dict.get('res_model'), 'school.issue')
        action_dict = self.student.button_open_school_claims()
        self.assertIn(
            ('student_id', 'in', self.student.ids), action_dict.get('domain'))
        self.assertEquals(action_dict.get('res_model'), 'school.claim')
