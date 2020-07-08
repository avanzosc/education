# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.calendar_school.tests.\
    test_calendar_school import TestCalendarSchool


class TestEducationNotebookObservation(TestCalendarSchool):

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
        cls.edu_partner = cls.env['res.partner'].create({
            'name': 'Center for test e-n-o'})
        cls.edu_task_type = cls.env['education.task_type'].create({
            'education_code': 'TEST e-n-o',
            'description': 'Test Task Type e-n-o'})
        cls.edu_plan = cls.env['education.plan'].create({
            'education_code': 'TEST e-n-o',
            'description': 'Test Plan e-n-o'})
        cls.edu_level = cls.env['education.level'].create({
            'education_code': 'TEST e-n-o',
            'description': 'Test Level e-n-o',
            'plan_id': cls.edu_plan.id})
        cls.edu_field = cls.env['education.field'].create({
            'education_code': 'TEST e-n-o',
            'description': 'Test Field e-n-o'})
        cls.edu_subject = cls.env['education.subject'].create({
            'education_code': 'TESTTEST',
            'description': 'Test Subject',
            'level_field_ids': [(0, 0, {
                'level_id': cls.edu_level.id,
                'field_id': cls.edu_field.id,
            })],
            'level_course_ids': [(0, 0, {
                'course_id': cls.edu_course.id,
                'level_id': cls.edu_level.id,
                'plan_id': cls.edu_plan.id,
            })],
        })
        cls.schedule = cls.schedule_model.create({
            "center_id": cls.edu_partner.id,
            "academic_year_id": cls.academic_year.id,
            "teacher_id": cls.teacher.id,
            "task_type_id": cls.edu_task_type.id,
            "subject_id": cls.edu_subject.id,
            "group_ids": [(6, 0, cls.group.ids)]})
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
            "competence_id": cls.exam_competence.id,
            "evaluation_id": cls.academic_year.evaluation_ids[0].id})
        vals = {
            'academic_year_id': cls.academic_year.id,
            'n_line_id': cls.exam_line.id,
            'student_id': cls.student.id,
            'teacher': cls.teacher.id}
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

    def test_calendar_school(self):
        """Don't repeat this test."""
        pass

    def test_calendar_school_wizard(self):
        """Don't repeat this test."""
        pass
