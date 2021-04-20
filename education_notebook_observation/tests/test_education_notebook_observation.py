# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from .common import EducationNotebookObservation
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestEducationNotebookObservation(EducationNotebookObservation):

    def test_education_notebook_observation(self):
        self.assertEquals(self.student.student_count_meetings, 0)
        self.assertEquals(self.family.family_count_meetings, 0)
        self.assertEquals(self.teacher.count_meetings, 0)
        self.assertEquals(self.tutor.count_meetings, 0)
        self.tutor.generate_meetings()
        cond = [('student_id', '=', self.student.id)]
        calendar = self.calendar_model.search(cond, limit=1)
        field_list = self.wiz_model.fields_get_keys()
        convert_vals = self.wiz_model.with_context(
            active_id=calendar.id).default_get(field_list)
        wiz = self.wiz_model.create(convert_vals)
        self.assertEqual(
            len(calendar.calendar_event_notebook_observation_ids), 0)
        wiz.with_context(
            active_id=calendar.id).button_generate_notebook_observations()
        self.assertEqual(
            len(calendar.calendar_event_notebook_observation_ids), 1)
        self.assertEqual(self.teacher.count_notebook_observation, 1)
        observation = calendar.calendar_event_notebook_observation_ids[0]
        observation.write({'observations': 'aaaaaaaaaaaaaaaaa'})
        self.assertEqual(observation.state, 'included')
        domain = [('teacher_id', 'in', [self.teacher.id])]
        res = self.teacher.button_show_notebook_observations()
        self.assertEqual(res.get('domain'), domain)
