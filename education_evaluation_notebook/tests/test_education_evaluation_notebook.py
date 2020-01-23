# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import EducationNotebookCommon
from odoo import fields
from odoo.exceptions import RedirectWarning, ValidationError
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestEducationEvaluationNotebook(EducationNotebookCommon):

    def test_education_competence_evaluation_constraint(self):
        with self.assertRaises(ValidationError):
            self.competence_model.create({
                "name": "Evaluation competence",
                "eval_mode": "both",
                "evaluation_check": True,
            })

    def test_education_competence_global_constraint(self):
        with self.assertRaises(ValidationError):
            self.competence_model.create({
                "name": "Global competence",
                "eval_mode": "both",
                "global_check": True,
            })

    def test_schedule_homework(self):
        self.assertFalse(self.schedule.homework_count)
        self.homework_model.create({
            "schedule_id": self.schedule.id,
            "name": "Test Homework",
            "date": fields.Date.context_today(self.schedule),
        })
        self.assertEquals(self.schedule.homework_count, 1)
        homework_dict = self.schedule.button_show_homework()
        self.assertIn(
            ("schedule_id", "=", self.schedule.id),
            homework_dict.get("domain"))

    def test_manual_create_notebook(self):
        self.create_evaluations()
        first_eval = self.academic_year.evaluation_ids[:1]
        self.assertEquals(first_eval.eval_type, "first")
        notebook = self.notebook_model.new({
            "competence_id": self.exam_competence.id,
            "evaluation_id": self.academic_year.evaluation_ids[:1],
        })
        self.assertNotEquals(notebook.description, self.exam_competence.name)
        notebook._onchange_competence_id()
        self.assertEquals(notebook.description, self.exam_competence.name)
        self.assertNotEquals(notebook.eval_type, first_eval.eval_type)
        notebook._onchange_evaluation_id()
        self.assertEquals(notebook.eval_type, first_eval.eval_type)
        self.assertEquals(
            notebook.display_name,
            "{} [{}]".format(notebook.description, notebook.eval_type))

    def test_create_notebook(self):
        self.create_evaluations()
        evaluation_count = len(self.academic_year.evaluation_ids)
        self.assertFalse(self.schedule.notebook_line_count)
        self.assertFalse(self.schedule.record_count)
        self.schedule.action_generate_notebook_lines()
        self.schedule.action_generate_records()
        student_count = self.schedule.student_count
        self.assertEquals(
            self.schedule.notebook_line_count, evaluation_count + 1)
        line_act_dict = self.schedule.button_show_notebook_lines()
        self.assertIn(
            ("schedule_id", "=", self.schedule.id),
            line_act_dict.get("domain"))
        self.assertEquals(
            self.schedule.record_count, (evaluation_count + 1) * student_count)
        self.assertEquals(
            self.edu_student.academic_record_count,
            (evaluation_count + 1) * student_count)
        record_act_dict = self.edu_student.button_show_student_records()
        self.assertIn(
            ("student_id", "=", self.edu_student.id),
            record_act_dict.get("domain"))
        global_records = self.schedule.record_ids.filtered("global_competence")
        self.assertEquals(len(global_records), student_count)
        for global_record in global_records:
            self.assertEquals(
                global_record.child_record_count, evaluation_count)
            record_dict = global_record.button_show_records()
            self.assertIn(
                ("id", "in", global_record.child_record_ids.ids),
                record_dict.get("domain"))
            self.assertEquals(
                global_record.mark_id, self.mark_model.search([
                    ("initial_mark", "<=", global_record.numeric_mark),
                    ("final_mark", ">=", global_record.numeric_mark)], limit=1)
            )
        eval_records = self.schedule.record_ids.filtered(
            "evaluation_competence")
        self.assertEquals(len(eval_records), evaluation_count * student_count)
        record_act_dict = self.schedule.button_show_records()
        self.assertIn(
            ("n_line_id", "in", self.schedule.notebook_line_ids.ids),
            record_act_dict.get("domain"))
        exam_act_dict = self.schedule.button_show_exams()
        self.assertIn(
            ("schedule_id", "=", self.schedule.id),
            exam_act_dict.get("domain"))
        homework_act_dict = self.schedule.button_show_homework()
        self.assertIn(
            ("schedule_id", "=", self.schedule.id),
            homework_act_dict.get("domain"))
        evaluation_lines = self.schedule.notebook_line_ids.filtered(
            "evaluation_competence")
        for evaluation_line in evaluation_lines:
            exam_line = self.notebook_model.create({
                "description": "Exam Line for {}".format(
                    evaluation_line.description),
                "schedule_id": self.schedule.id,
                "parent_line_id": evaluation_line.id,
                "competence_id": self.exam_competence.id,
            })
            self.assertFalse(exam_line.evaluation_id)
            exam_line._onchange_parent_line_id()
            self.assertEquals(exam_line.evaluation_id,
                              exam_line.parent_line_id.evaluation_id)
            exam_line.button_create_student_records()
            self.assertFalse(exam_line.exam_count)
            self.assertEquals(exam_line.record_count, student_count)
            exam_record_dict = exam_line.button_show_records()
            self.assertIn(
                ("n_line_id", "=", exam_line.id),
                exam_record_dict.get("domain"))
            exam_line.write({
                "exam_ids": [(0, 0, {
                    "name": "Test Exam",
                    "exam_type_id": self.exam_type.id,
                    "eval_percent": 100.0,
                })]
            })
            self.assertEquals(exam_line.exam_count, 1)
            exam_line.button_create_student_records()
            self.assertEquals(
                exam_line.record_count, 2 * student_count)
            exam = exam_line.exam_ids[:1]
            self.assertEquals(
                exam.record_count, student_count)
            exam_act_dict = exam.button_show_records()
            self.assertIn(
                ("exam_id", "=", exam.id), exam_act_dict.get("domain"))
            self.assertFalse(exam.date)
            self.assertEquals(exam.state, "draft")
            for exam_record in exam.record_ids:
                self.assertEquals(exam_record.exam_state, exam.state)
            with self.assertRaises(ValidationError):
                exam.action_marking()
            today = fields.Date.context_today(exam)
            exam.date = today
            exam.action_marking()
            self.assertEquals(exam.state, "progress")
            exam.action_draft()
            self.assertEquals(exam.state, "draft")
            exam.action_marking()
            exam.action_graded()
            self.assertEquals(exam.state, "done")
            exam.action_close_exam()
            self.assertEquals(exam.state, "closed")
            self.assertEquals(exam.mark_close_date, today)

    def create_evaluations(self):
        self.assertFalse(self.academic_year.evaluation_ids)
        academic_year = self.academic_year.copy(default={
            "name": "TEST_YEAR",
            "date_start": False,
            "date_end": False,
        })
        create_eval_dict = self.create_eval_model.with_context(
            active_model=self.course_change._name,
            active_ids=self.course_change.ids).default_get(
            self.create_eval_model.fields_get_keys())
        create_eval_dict.update({
            "academic_year_id": academic_year.id,
            "evaluation_number": 3,
            "final_evaluation": True,
        })
        self.assertEquals(
            [(6, 0, self.course_change.ids)],
            create_eval_dict.get("course_change_ids"))
        create_eval = self.create_eval_model.create(create_eval_dict)
        with self.assertRaises(RedirectWarning):
            create_eval.button_create_evaluation()
        create_eval.academic_year_id = self.academic_year
        create_eval.button_create_evaluation()
        self.assertEquals(len(self.academic_year.evaluation_ids), 4)

    def test_create_evaluations_without_wizard(self):
        with self.assertRaises(RedirectWarning):
            self.course_change.create_evaluations()
