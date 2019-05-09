# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationGroup(models.Model):
    _name = 'education.group'
    _inherit = 'education.data'
    _description = 'Education Group'

    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        required=True)
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        required=True)
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Plan')
    level_id = fields.Many2one(
        comodel_name='education.level', string='Level',
        domain="[('plan_id', '=', plan_id)]")
    field_id = fields.Many2one(
        comodel_name='education.field', string='Study Field')
    classroom_id = fields.Many2one(
        comodel_name='education.classroom', string='Classroom',
        domain="[('center_id', '=', center_id)]")
    shift_id = fields.Many2one(
        comodel_name='education.shift', string='Shift')
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course',
        domain="[('plan_id', '=', plan_id), ('level_id', '=', level_id),"
               "('field_id', '=', field_id), ('shift_id', '=', shift_id)]")
    model_id = fields.Many2one(
        comodel_name='education.model', string='Educational Model')
    group_type_id = fields.Many2one(
        comodel_name='education.group_type', string='Educational Group Type')
    calendar_id = fields.Many2one(
        comodel_name='resource.calendar', string='Calendar',
        domain="[('center_id', '=', center_id)]")
    comments = fields.Text(string='Comments')
    teacher_ids = fields.One2many(
        comodel_name='education.group.teacher',
        inverse_name='group_id', string='Teachers')
    student_ids = fields.Many2many(
        comodel_name='res.partner', relation='edu_group_student',
        column1='group_id', column2='student_id', string='Students')

    _sql_constraints = [
        ('education_code_unique',
         'unique(education_code,center_id,academic_year_id)',
         'Education code must be unique per center and academic year!'),
    ]


class EducationGroupTeacher(models.Model):
    _name = 'education.group.teacher'
    _description = 'Education Group Teachers'

    group_id = fields.Many2one(
        comodel_name='education.group', required=True, ondelete='cascade')
    employee_id = fields.Many2one(comodel_name='hr.employee')
    sequence = fields.Integer(string='Sequence')

    _sql_constraints = [
        ('group_sequence_unique',
         'unique(group_id,sequence)',
         'Sequence must be unique per group!'),
        ('sequence_one2ten', 'check(sequence between 1 and 10)',
         'Sequence must be between 1 and 10!'),
    ]
