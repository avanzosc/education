# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    next_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='school_id',
        string='Next Courses')
    prev_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='next_school_id',
        string='Previous Courses')
    alumni_center_id = fields.Many2one(
        comodel_name='res.partner', string='Last Education Center',
        domain=[('educational_category', '=', 'school')])
    alumni_academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Last Academic Year')
    alumni_member = fields.Boolean(string='Alumni Association Member')
    student_group_ids = fields.Many2many(
        comodel_name='education.group', relation='edu_group_student',
        column1='student_id', column2='group_id', string='Education Groups',
        readonly=True)
