# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.calendar_school.tests.common import TestCalendarSchoolCommon


class EducationNotebookObservation(TestCalendarSchoolCommon):

    @classmethod
    def setUpClass(cls):
        super(EducationNotebookObservation, cls).setUpClass()
        cls.wiz_model = cls.env['wiz.generate.notebook.observation']
        cls.wiz_mail_model = cls.env['wiz.send.notebook.observation.email']
        cls.notebook_model = cls.env["education.notebook.line"]
        cls.schedule_model = cls.env['education.schedule']
        cls.competence_model = cls.env["education.competence"]
        cls.evaluation_model = cls.env['education.academic_year.evaluation']
        cls.record_model = cls.env['education.record']
        cls.message_model = cls.env['mail.message']
        cls.mail_model = cls.env['mail.mail']
        cls.eval_competence = cls.competence_model.search([
            ("evaluation_check", "=", True)])
        if not cls.eval_competence:
            cls.competence_model.create({
                "name": "Evaluation Competence",
                "evaluation_check": True,
            })
        cls.evaluation_model.create({
            'name': 'Evaluation',
            'academic_year_id': cls.academic_year.id,
            'center_id': cls.tutor.center_id.id,
            'course_id': cls.tutor.course_id.id,
            'date_start': cls.academic_year.date_start,
            'date_end': cls.academic_year.date_end,
            'eval_type': 'third'})
        cls.notebook_line = cls.notebook_model.create({
            "description": "Exam Line for test e-n-o",
            "teacher_id": cls.teacher.id,
            "a_year_id": cls.academic_year.id,
            "eval_type": "third",
            "schedule_id": cls.schedule.id,
            "competence_id": cls.eval_competence.id})
        vals = {
            'academic_year_id': cls.academic_year.id,
            'n_line_id': cls.notebook_line.id,
            'student_id': cls.student.id,
        }
        cls.record = cls.record_model.create(vals)
