# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationProvision(models.Model):
    _name = 'education.provision'
    _description = 'Education Provision'

    education_code = fields.Char(string='Code')
    edu_level_course_subject_id = fields.Many2one(
        comodel_name='education.level.course.subject',
        string='Education Level, Course and Subject Relation')
    level_id = fields.Many2one(
        comodel_name='education.level', string='Level',
        related='edu_level_course_subject_id.level_id')
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course',
        related='edu_level_course_subject_id.course_id')
    subject_id = fields.Many2one(
        comodel_name='education.subject', string='Education Subject',
        related='edu_level_course_subject_id.subject_id')
    classroom_id = fields.Many2one(
        comodel_name='education.classroom', string='Classroom')
    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Teacher')
    student_ids = fields.Many2many(
        comodel_name='res.partner', relation='edu_provision_student',
        column1='provision_id', column2='student_id', string='Students',
        domain=[('educational_category', '=', 'student')])
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year')
    school_id = fields.Many2one(
        comodel_name='res.partner', string='School',
        domain=[('educational_category', '=', 'school')])
    comments = fields.Text(string='Comments')
