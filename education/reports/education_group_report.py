# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs


class EducationGroupReport(models.Model):
    _name = 'education.group.report'
    _description = 'Groups Report'
    _auto = False
    _rec_name = 'student_id'
    _order = "academic_year_id,center_id,group_id,student_id"

    student_id = fields.Many2one(
        comodel_name='res.partner', string='Student')
    student_firstname = fields.Char(string="Student's Firstname")
    student_lastname = fields.Char(string="Student's First Lastname")
    student_lastname2 = fields.Char(string="Student's Second Lastname")
    group_id = fields.Many2one(
        comodel_name='education.group', string='Education Group')
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year')
    group_type_id = fields.Many2one(
        comodel_name='education.group_type', string='Educational Group Type')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center')
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course')

    _depends = {
        'education.group': [
            'center_id', 'course_id', 'group_type_id', 'academic_year_id',
            'student_ids',
        ],
    }

    def _select(self):
        select_str = """
            SELECT
                row_number() OVER () as id,
                stu.id AS student_id,
                stu.lastname AS student_lastname,
                stu.lastname2 AS student_lastname2,
                stu.firstname AS student_firstname,
                grp.id AS group_id,
                grp.group_type_id AS group_type_id,
                grp.academic_year_id AS academic_year_id,
                grp.center_id AS center_id,
                grp.course_id AS course_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM edu_group_student student_grp
                JOIN res_partner stu ON student_grp.student_id = stu.id
                JOIN education_group grp ON student_grp.group_id = grp.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY stu.id, grp.id, grp.group_type_id,
                grp.academic_year_id, grp.center_id, grp.course_id,
                stu.firstname, stu.lastname, stu.lastname2
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = education_group_teacher_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as
                (
                %s %s %s
            )""", (
                AsIs(self._table), AsIs(self._select()), AsIs(self._from()),
                AsIs(self._group_by()),))
