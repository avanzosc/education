# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.education.tests.common import TestEducationCommon


class EducationNotebookCommon(TestEducationCommon):

    @classmethod
    def setUpClass(cls):
        super(EducationNotebookCommon, cls).setUpClass()
        cls.competence_model = cls.env["education.competence"]
        cls.exam_model = cls.env["education.exam"]
        cls.notebook_model = cls.env["education.notebook.line"]
        cls.homework_model = cls.env["education.homework"]
        cls.mark_model = cls.env["education.mark.numeric"]
        cls.create_eval_model = cls.env["create.academic_year.evaluation"]
        cls.report_wizard_model = cls.env[
            "report.education.education_record_xlsx.export"]
        cls.edu_partner.educational_category = "school"
        cls.edu_student = cls.env["res.partner"].create({
            "name": "Test Student",
            "educational_category": "student",
        })
        cls.group = cls.group_model.create({
            "education_code": "TEST",
            "description": "Test Group",
            "center_id": cls.edu_partner.id,
            "academic_year_id": cls.academic_year.id,
            "plan_id": cls.edu_plan.id,
            "level_id": cls.edu_level.id,
            "course_id": cls.edu_course.id,
            "group_type_id": cls.edu_group_type.id,
            "student_ids": [(6, 0, cls.edu_student.ids)],
        })
        task_type = cls.env['education.task_type'].search([
            ("education_code", "=", "0120")]) or cls.edu_task_type
        if task_type.education_code != "0120":
            task_type.write({
                "education_code": "0120",
            })
        cls.schedule = cls.schedule_model.create({
            "center_id": cls.edu_partner.id,
            "academic_year_id": cls.academic_year.id,
            "teacher_id": cls.teacher.id,
            "task_type_id": task_type.id,
            "subject_id": cls.edu_subject.id,
            "group_ids": [(6, 0, cls.group.ids)],
        })
        cls.exam_competence = cls.competence_model.create({
            "name": "Exam Competence",
        })
        cls.notebook_template = cls.env["education.notebook.template"].create({
            "code": "TMP",
            "education_center_id": cls.schedule.center_id.id,
            "course_id": cls.edu_course.id,
            "task_type_id": cls.schedule.task_type_id.id,
            "subject_id": cls.schedule.subject_id.id,
            "eval_type": "first",
            "competence_id": cls.exam_competence.id,
            "name": "Notebook Template",
            "eval_percent": 50.0,
        })
        cls.exam_type = cls.env["education.exam.type"].create({
            "name": "Test Control Type",
            "e_type": "control",
        })
        cls.new_course = cls.edu_course.copy(
            default={"education_code": "TES2"})
        cls.course_change = cls.env["education.course.change"].create({
            "school_id": cls.edu_partner.id,
            "course_id": cls.new_course.id,
            "next_school_id": cls.edu_partner.id,
            "next_course_id": cls.edu_course.id,
        })
