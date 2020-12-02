# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import EducationNotebookCommon
from odoo import _, fields
from odoo.exceptions import RedirectWarning, UserError, ValidationError
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

    def test_education_competence_code_length(self):
        with self.assertRaises(ValidationError):
            self.competence_model.create({
                "code": "TEST",
                "name": "Competence",
                "eval_mode": "both",
            })

    def test_education_notebook_template_code_length(self):
        with self.assertRaises(ValidationError):
            self.env["education.notebook.template"].create({
                "code": "CODE",
                "education_center_id": self.edu_partner.id,
                "course_id": self.edu_course.id,
                "task_type_id": self.edu_task_type.id,
                "subject_id": self.edu_subject.id,
                "eval_type": "first",
                "competence_id": self.exam_competence.id,
                "name": "Notebook Template",
                "eval_percent": 50.0,
            })

    def test_education_notebook_line_code_length(self):
        with self.assertRaises(ValidationError):
            self.notebook_model.create({
                "code": "CODE",
                "description": "Notebook Line",
                "education_center_id": self.edu_partner.id,
                "task_type_id": self.edu_task_type.id,
                "subject_id": self.edu_subject.id,
                "eval_type": "first",
                "competence_id": self.exam_competence.id,
                "eval_percent": 50.0,
                "schedule_id": self.schedule.id,
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
        self.create_evaluations_from_course_change()
        notebook = self.notebook_model.new({
            "competence_id": self.exam_competence.id,
        })
        self.assertNotEquals(notebook.description, self.exam_competence.name)
        notebook._onchange_competence_id()
        self.assertEquals(notebook.description, self.exam_competence.name)
        field = notebook._fields["eval_type"]
        eval_type = field.convert_to_export(notebook["eval_type"], notebook)
        self.assertEquals(
            notebook.display_name,
            "{} [{}]".format(notebook.description, eval_type))

    def test_get_evaluation_records(self):
        self.create_evaluations_from_course_change(final_eval=False)
        evaluation_count = len(self.academic_year.evaluation_ids)
        self.schedule.action_generate_notebook_lines()
        self.schedule.action_generate_records()
        student_count = self.schedule.student_count
        notebook_count = evaluation_count + 2
        self.assertEquals(
            self.schedule.notebook_line_count, notebook_count)
        eval_records = self.schedule.record_ids.filtered(
            "evaluation_competence")
        self.assertEquals(len(eval_records), evaluation_count * student_count)
        for student in self.schedule.student_ids:
            student_eval_records = eval_records.filtered(
                lambda r: r.student_id == student)
            self.assertEquals(len(student_eval_records), evaluation_count)
            records = student.get_academic_records()
            self.assertIn(records, student_eval_records)
        for eval_record in eval_records:
            eval_record.button_set_assessed()
            retake_eval_dict = eval_record.button_retake()
            self.assertIn(retake_eval_dict.get("res_id"),
                          eval_record.retake_record_ids.ids)
            for retake_record in eval_record.retake_record_ids:
                self.assertEquals(
                    "[RETAKE] {} - {}".format(
                        retake_record.n_line_id.display_name,
                        retake_record.student_id.display_name),
                    retake_record.display_name)
            show_retake_dict = eval_record.with_context(
                retake=True).button_show_records()
            self.assertIn(
                ("id", "in", eval_record.retake_record_ids.ids),
                show_retake_dict.get("domain"))

    def test_create_notebook(self):
        self.create_evaluations_from_course_change(final_eval=False)
        evaluation_count = len(self.academic_year.evaluation_ids)
        self.assertFalse(self.schedule.notebook_line_count)
        self.assertFalse(self.schedule.record_count)
        self.schedule.action_generate_notebook_lines()
        self.schedule.action_generate_records()
        student_count = self.schedule.student_count
        notebook_count = evaluation_count + 2
        self.assertEquals(
            self.schedule.notebook_line_count, notebook_count)
        self.schedule.action_generate_notebook_lines()
        self.assertEquals(
            self.schedule.notebook_line_count, notebook_count)
        line_act_dict = self.schedule.button_show_notebook_lines()
        self.assertIn(
            ("schedule_id", "=", self.schedule.id),
            line_act_dict.get("domain"))
        global_line = self.schedule.notebook_line_ids.filtered(
            "global_competence")
        edit_action = global_line.button_open_notebook_line_form()
        self.assertEquals(
            "form", edit_action.get("view_mode"))
        self.assertIn(
            ("id", "=", global_line.id),
            edit_action.get("domain"))
        child_act_dict = global_line.button_show_child_lines()
        self.assertIn(
            ("parent_line_id", "=", global_line.id),
            child_act_dict.get("domain"))
        self.assertEquals(
            self.schedule.record_count, notebook_count * student_count)
        self.assertEquals(
            self.edu_student.academic_record_count, notebook_count)
        self.assertEquals(
            self.group.record_count,
            sum(self.group.mapped("student_ids.academic_record_count")))
        action_dict = self.group.button_show_records()
        self.assertIn(
            ("student_id", "in", self.group.student_ids.ids),
            action_dict.get("domain"))
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

            self.assertNotEquals(exam_line.eval_type,
                                 exam_line.parent_line_id.eval_type)
            exam_line._onchange_parent_line_id()
            self.assertEquals(exam_line.eval_type,
                              exam_line.parent_line_id.eval_type)
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
                exam_line.record_count, student_count)
            exam_line_record = exam_line.record_ids.filtered(
                lambda r: not r.exam_id)[:1]
            exam_record = exam_line.record_ids.filtered(
                lambda r: r.exam_id)[:1]
            self.assertEquals(
                exam_record.subject_name, exam_record.subject_id.description)
            with self.assertRaises(ValidationError):
                exam_record.numeric_mark = 12.5
            with self.assertRaises(ValidationError):
                exam_record.numeric_mark = -1.5
            exam_record.numeric_mark = 5.5
            self.assertEquals(exam_record.state, "initial")
            self.assertEquals(exam_record.pass_mark, "pass")
            self.assertEquals(
                exam_record.mark_id, self.env.ref(
                    "education_evaluation_notebook.numeric_mark_normal"))
            exam_record.button_set_assessed()
            self.assertEquals(exam_record.state, "assessed")
            self.assertNotEquals(
                exam_line_record.calculated_partial_mark,
                exam_line_record.numeric_mark)
            self.assertEquals(
                exam_line_record.calculated_numeric_mark,
                exam_record.numeric_mark)
            self.assertNotEquals(
                exam_line_record.calculated_numeric_mark,
                exam_line_record.numeric_mark)
            self.assertEquals(
                exam_line_record.calculated_numeric_mark,
                exam_record.numeric_mark * exam_record.exam_eval_percent / 100)
            self.assertEquals(exam_line_record.state, "initial")
            exam_line_record.action_copy_partial_calculated_mark()
            self.assertEquals(
                exam_line_record.calculated_partial_mark,
                exam_line_record.numeric_mark)
            exam_line_record.action_copy_calculated_mark()
            self.assertEquals(
                exam_line_record.calculated_numeric_mark,
                exam_line_record.numeric_mark)
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
            retake_action = exam.retake_exam()
            self.assertIn(retake_action.get("res_id"), exam.retake_ids.ids)
            self.assertEquals(exam.retake_count, 1)
            show_retake_action = exam.button_show_retakes()
            self.assertIn(
                ("recovered_exam_id", "=", exam.id),
                show_retake_action.get("domain"))
            retake_exam = exam.retake_ids[:1]
            self.assertEquals(
                retake_exam.display_name,
                _("[RETAKE] {}").format(retake_exam.name))
            new_retake_exam = self.exam_model.new({
                "recovered_exam_id": exam.id,
            })
            self.assertFalse(new_retake_exam.n_line_id)
            new_retake_exam._onchange_recovered_exam()
            self.assertEquals(new_retake_exam.n_line_id, exam.n_line_id)
            with self.assertRaises(UserError):
                exam.unlink()
            exam_record.button_set_draft()
            self.assertEquals(exam_record.state, "initial")
            exam_record.button_set_exempt()
            self.assertEquals(exam_record.exceptionality, "exempt")
            exam_record.button_set_assessed()
            exam_record.button_set_not_taken()
            self.assertEquals(exam_record.exceptionality, "exempt")
            exam_record.button_set_draft()
            self.assertEquals(exam_record.state, "initial")
            exam_record.button_set_not_taken()
            self.assertEquals(exam_record.exceptionality, "not_taken")
            exam_record.button_set_not_evaluated()
            self.assertEquals(exam_record.exceptionality, "not_evaluated")
            exam_record.button_set_adaptation()
            self.assertEquals(exam_record.exceptionality, "adaptation")
            exam_record.button_set_reinforcement()
            self.assertEquals(exam_record.exceptionality, "reinforcement")
            exam_record.button_remove_exceptionality()
            self.assertFalse(exam_record.exceptionality)
            exam_record.button_set_pending()
            self.assertEquals(exam_record.exceptionality, "pending")

    def create_evaluations_from_course_change(self, final_eval=True):
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
            "final_evaluation": final_eval,
        })
        self.assertEquals(len(create_eval_dict.get("line_ids")), 1)
        create_eval = self.create_eval_model.create(create_eval_dict)
        with self.assertRaises(RedirectWarning):
            create_eval.button_create_evaluation()
        with self.assertRaises(RedirectWarning):
            academic_year.create_evaluations(self.edu_partner, self.edu_course)
        create_eval.academic_year_id = self.academic_year
        create_eval.button_create_evaluation()
        if final_eval:
            self.assertEquals(len(self.academic_year.evaluation_ids), 4)
        else:
            self.assertEquals(len(self.academic_year.evaluation_ids), 3)

    def test_create_evaluations_from_education_center(self):
        self.assertFalse(self.academic_year.evaluation_ids)
        create_eval_dict = self.create_eval_model.with_context(
            active_model=self.edu_partner._name,
            active_ids=self.edu_partner.ids).default_get(
            self.create_eval_model.fields_get_keys())
        create_eval_dict.update({
            "academic_year_id": self.academic_year.id,
            "evaluation_number": 3,
            "final_evaluation": True,
        })
        self.assertEquals(len(create_eval_dict.get("line_ids")), 2)
        create_eval = self.create_eval_model.create(create_eval_dict)
        create_eval.button_create_evaluation()
        self.assertEquals(len(self.academic_year.evaluation_ids), 8)

    def test_create_evaluations_from_education_course(self):
        self.assertFalse(self.academic_year.evaluation_ids)
        create_eval_dict = self.create_eval_model.with_context(
            active_model=self.edu_course._name,
            active_ids=self.edu_course.ids).default_get(
            self.create_eval_model.fields_get_keys())
        create_eval_dict.update({
            "academic_year_id": self.academic_year.id,
            "evaluation_number": 3,
            "final_evaluation": True,
        })
        self.assertEquals(len(create_eval_dict.get("line_ids")), 1)
        create_eval = self.create_eval_model.create(create_eval_dict)
        create_eval.button_create_evaluation()
        self.assertEquals(len(self.academic_year.evaluation_ids), 4)

    def test_create_evaluations(self):
        self.assertFalse(self.academic_year.evaluation_ids)
        create_eval_dict = self.create_eval_model.default_get(
            self.create_eval_model.fields_get_keys())
        create_eval_dict.update({
            "academic_year_id": self.academic_year.id,
            "evaluation_number": 3,
            "final_evaluation": False,
        })
        self.assertEquals(len(create_eval_dict.get("line_ids")), 1)
        create_eval = self.create_eval_model.create(create_eval_dict)
        create_eval.button_create_evaluation()
        self.assertEquals(len(self.academic_year.evaluation_ids), 3)

    def test_course_change(self):
        self.assertFalse(self.course_change.eval_count)
        self.assertFalse(self.course_change.next_eval_count)
        current_year = self.academic_year_model.search([
            ("current", "=", True)])
        if not current_year:
            current_year = self.academic_year_model.create({
                "name": "TEST_YEAR",
                "date_start": self.today.replace(month=1, day=1),
                "date_end": self.today.replace(month=12, day=31),
            })
        self.assertTrue(current_year and current_year.current)
        self.assertFalse(current_year.evaluation_ids)
        current_year.create_evaluations(
            self.course_change.next_school_id,
            self.course_change.next_course_id,
            evaluation_number=3,
            final_evaluation=True)
        self.assertEquals(len(current_year.evaluation_ids), 4)
        self.course_change.invalidate_cache()
        self.assertEquals(self.course_change.eval_count, 4)
        self.assertEquals(self.course_change.next_eval_count, 0)
        current, next_year = self.course_change._get_academic_years()
        action_dict = self.course_change.button_open_current_evaluations()
        self.assertIn(
            ('academic_year_id', '=', current.id), action_dict.get('domain'))
        self.assertIn(
            ('center_id', '=', self.course_change.next_school_id.id),
            action_dict.get('domain'))
        self.assertIn(
            ('course_id', '=', self.course_change.next_course_id.id),
            action_dict.get('domain'))
        action_dict = self.course_change.button_open_next_evaluations()
        self.assertIn(
            ('academic_year_id', '=', next_year.id), action_dict.get('domain'))
        self.assertIn(
            ('center_id', '=', self.course_change.next_school_id.id),
            action_dict.get('domain'))
        self.assertIn(
            ('course_id', '=', self.course_change.next_course_id.id),
            action_dict.get('domain'))

    def test_education_group_record_report_xlsx(self):
        self.create_evaluations_from_course_change(final_eval=False)
        report_name = (
            "education_evaluation_notebook.education_group_record_xlsx")
        self.schedule.action_generate_notebook_lines()
        self.schedule.action_generate_records()
        report_xlsx = self.env.ref(report_name).render(
            self.schedule.group_ids.ids)
        self.assertGreaterEqual(len(report_xlsx[0]), 1)
        self.assertEqual(report_xlsx[1], "xlsx")

    def test_education_group_record_report_xlsx_wizard(self):
        self.create_evaluations_from_course_change(final_eval=False)
        self.schedule.action_generate_notebook_lines()
        self.schedule.action_generate_records()
        wizard = self.report_wizard_model.with_context(
            active_ids=self.schedule.group_ids.ids).create({
                "eval_type": "first",
            })
        wizard_return = wizard.export_xls()
        self.assertEqual(wizard_return["report_type"], "xlsx")
