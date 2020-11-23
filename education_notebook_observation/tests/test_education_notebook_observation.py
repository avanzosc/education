# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common
from odoo.addons.calendar_school.tests.common import TestCalendarSchoolCommon


@common.at_install(False)
@common.post_install(True)
class TestEducationNotebookObservation(TestCalendarSchoolCommon):

    @classmethod
    def setUpClass(cls):
        super(TestEducationNotebookObservation, cls).setUpClass()
        cls.wiz_model = cls.env['wiz.generate.notebook.observation']
        cls.wiz_mail_model = cls.env['wiz.send.notebook.observation.email']
        cls.notebook_model = cls.env["education.notebook.line"]
        cls.schedule_model = cls.env['education.schedule']
        cls.competence_model = cls.env["education.competence"]
        cls.evaluation_model = cls.env['education.academic_year.evaluation']
        cls.record_model = cls.env['education.record']
        cls.message_model = cls.env['mail.message']
        cls.mail_model = cls.env['mail.mail']
        cls.exam_competence = cls.competence_model.create({
            "name": "Exam Competence e-n-o"})
        cls.evaluation_model.create({
            'name': 'Evaluation',
            'academic_year_id': cls.tutor.school_year_id.id,
            'center_id': cls.tutor.center_id.id,
            'course_id': cls.tutor.course_id.id,
            'date_start': cls.academic_year.date_start,
            'date_end': cls.academic_year.date_end,
            'eval_type': 'third'})
        cls.exam_line = cls.notebook_model.create({
            "description": "Exam Line for test e-n-o",
            "teacher_id": cls.teacher.id,
            "a_year_id": cls.academic_year.id,
            "eval_type": "third",
            "schedule_id": cls.schedule.id,
            "competence_id": cls.exam_competence.id})
        vals = {
            'academic_year_id': cls.academic_year.id,
            'n_line_id': cls.exam_line.id,
            'student_id': cls.student.id
        }
        cls.record = cls.record_model.create(vals)

    def test_education_notebook_observation(self):
        self.assertEquals(self.student.student_count_meetings, 0)
        self.assertEquals(self.family.family_count_meetings, 0)
        self.assertEquals(self.teacher.count_meetings, 0)
        self.assertEquals(self.tutor.count_meetings, 0)
        self.tutor.generate_meetings()
        cond = [('student_id', '=', self.student.id)]
        calendars = self.calendar_model.search(cond)
        school_year_id = calendars[0].supervised_year_id.school_year_id
        competences = self.env['education.competence'].search([])
        competences.write({'evaluation_check': False})
        cond = [('academic_year_id', '=', school_year_id.id),
                ('student_id', '=', calendars[0].student_id.id),
                ('n_line_id.competence_id', '!=', False)]
        records = self.env['education.record'].search(cond)
        for record in records:
            if record.n_line_id.competence_id:
                record.n_line_id.competence_id.evaluation_check = True
        field_list = self.wiz_model.fields_get_keys()
        convert_vals = self.wiz_model.with_context(
            active_id=calendars[0].id).default_get(field_list)
        wiz = self.wiz_model.create(convert_vals)
        self.assertEqual(
            len(calendars[0].calendar_event_notebook_observation_ids), 0)
        wiz.with_context(
            active_id=calendars[0].id).button_generate_notebook_observations()
        self.assertEqual(
            len(calendars[0].calendar_event_notebook_observation_ids), 1)
        self.assertEqual(self.teacher.count_notebook_observation, 1)
        cond = [('subject', 'ilike', '%Request for observations for student%')]
        message = self.message_model.search(cond)
        self.assertEqual(len(message), 0)
        wiz_mail = self.wiz_mail_model.create({})
        wiz_mail.with_context(
            active_id=calendars[0].id).button_send_email()
        message = self.message_model.search(cond)
        self.assertEqual(len(message), 1)
        observation = calendars[0].calendar_event_notebook_observation_ids[0]
        observation.write({'observations': 'aaaaaaaaaaaaaaaaa'})
        self.assertEqual(observation.state, 'included')
        domain = [('teacher_id', 'in', [self.teacher.id])]
        res = self.teacher.button_show_notebook_observations()
        self.assertEqual(res.get('domain'), domain)
