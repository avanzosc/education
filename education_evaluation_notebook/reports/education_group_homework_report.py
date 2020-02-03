# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs


class EducationGroupHomeworkReport(models.Model):
    _name = "education.group.homework.report"
    _inherit = "education.group.student.report"
    _description = "Groups Homework Report"
    _auto = False
    _rec_name = "student_id"

    homework_id = fields.Many2one(
        comodel_name="education.homework", string="Homework")
    homework_description = fields.Char(string="Homework Description")
    homework_deadline = fields.Date(string="Homework Deadline")

    _depends = {
        "education.schedule": [
            "subject_id", "classroom_id", "teacher_id", "academic_year_id"
        ],
        "education.group": [
            "center_id", "course_id", "student_ids"
        ],
    }

    def _select(self):
        select_str = """
                , edu_hw.id AS homework_id
                , edu_hw.name AS homework_description
                , edu_hw.date AS homework_deadline
        """
        return super(EducationGroupHomeworkReport, self)._select() + select_str

    def _from(self):
        from_str = """
                JOIN education_homework edu_hw ON edu_hw.schedule_id = sch.id
        """
        return super(EducationGroupHomeworkReport, self)._from() + from_str

    def _group_by(self):
        group_by_str = """
                , edu_hw.id, edu_hw.name, edu_hw.date
        """
        return (super(EducationGroupHomeworkReport, self)._group_by() +
                group_by_str)

    @api.model_cr
    def init(self):
        # self._table = education_group_homework_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as
                (
                %s %s %s
            )""", (
                AsIs(self._table), AsIs(self._select()), AsIs(self._from()),
                AsIs(self._group_by()),))
