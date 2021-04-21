# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs

from ..models.education_exam import EXAM_STATES


class EducationGroupStudentExamReport(models.Model):
    _name = "education.group.student.exam.report"
    _inherit = "education.group.student.report"
    _description = "Groups Exams Report for Student"
    _auto = False
    _rec_name = "student_id"

    exam_id = fields.Many2one(
        comodel_name="education.homework", string="Exam")
    exam_description = fields.Char(string="Exam Description")
    exam_date = fields.Date(string="Exam Date")
    exam_state = fields.Selection(selection=EXAM_STATES, string="Status")

    _depends = {
        "education.schedule": [
            "subject_id", "classroom_id", "teacher_id", "academic_year_id"
        ],
        "education.group": [
            "center_id", "course_id", "student_ids"
        ],
    }

    def _coalesce(self):
        return super(EducationGroupStudentExamReport, self)._coalesce()

    def _select(self):
        select_str = """
                , edu_exam.id AS exam_id
                , edu_exam.name AS exam_description
                , edu_exam.date AS exam_date
                , edu_exam.state AS exam_state
        """
        return (super(EducationGroupStudentExamReport, self)._select() +
                select_str)

    def _from(self):
        from_str = """
                JOIN education_exam edu_exam ON edu_exam.schedule_id = sch.id
        """
        return super(EducationGroupStudentExamReport, self)._from() + from_str

    def _group_by(self):
        group_by_str = """
                , edu_exam.id, edu_exam.name, edu_exam.date, edu_exam.state
        """
        return (super(EducationGroupStudentExamReport, self)._group_by() +
                group_by_str)

    @api.model_cr
    def init(self):
        # self._table = education_group_student_exam_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as
                (
                %s %s %s %s
            )""", (
                AsIs(self._table), AsIs(self._select()),
                AsIs(self._coalesce()), AsIs(self._from()),
                AsIs(self._group_by()),))
