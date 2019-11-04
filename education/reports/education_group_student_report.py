# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs


class EducationGroupStudentReport(models.Model):
    _name = 'education.group.student.report'
    _inherit = 'education.group.teacher.report'
    _description = 'Student Groups Report'
    _auto = False
    _rec_name = 'student_id'

    student_id = fields.Many2one(
        comodel_name='res.partner', string='Student')

    _depends = {
        'education.schedule': [
            'subject_id', 'classroom_id', 'teacher_id', 'academic_year_id'
        ],
        'education.group': [
            'center_id', 'course_id', 'student_ids'
        ],
    }

    def _select(self):
        select_str = """
                , stu_group.student_id AS student_id
        """
        return super(EducationGroupStudentReport, self)._select() + select_str

    def _from(self):
        from_str = """
                JOIN edu_group_student stu_group ON grp.id = stu_group.group_id
        """
        return super(EducationGroupStudentReport, self)._from() + from_str

    def _group_by(self):
        group_by_str = """
                , stu_group.student_id
        """
        return (super(EducationGroupStudentReport, self)._group_by() +
                group_by_str)

    @api.model_cr
    def init(self):
        # self._table = education_group_student_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as
                (
                %s %s %s
            )""", (
                AsIs(self._table), AsIs(self._select()), AsIs(self._from()),
                AsIs(self._group_by()),))
