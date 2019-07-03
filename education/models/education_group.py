# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        domain="[('plan_id', '=', plan_id)]", required=True)
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
    session_ids = fields.One2many(
        comodel_name='education.group.session', inverse_name='group_id',
        string='Sessions')
    student_ids = fields.Many2many(
        comodel_name='res.partner', relation='edu_group_student',
        column1='group_id', column2='student_id', string='Students')
    student_count = fields.Integer(
        string='Student Number', compute='_compute_student_count', store=True)
    parent_id = fields.Many2one(
        comodel_name='education.group', string='Parent Group',
        domain="[('academic_year_id', '=', academic_year_id),"
               "('center_id', '=', center_id),"
               "('course_id', '=', course_id),"
               "('group_type_id.type', '=', 'official')]")

    _sql_constraints = [
        ('education_code_unique',
         'unique(education_code,center_id,academic_year_id)',
         'Education code must be unique per center and academic year!'),
    ]

    @api.constrains('parent_id')
    def _check_group_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive groups.'))

    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)


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


class EducationGroupSession(models.Model):
    _name = 'education.group.session'
    _description = 'Education Group Sessions'
    _order = 'group_id,dayofweek,session_number'

    @api.model
    def _get_selection_dayofweek(self):
        return self.env['resource.calendar.attendance'].fields_get(
            allfields=['dayofweek'])['dayofweek']['selection']

    def default_dayofweek(self):
        default_dict = self.env['resource.calendar.attendance'].default_get([
            'dayofweek'])
        return default_dict.get('dayofweek')

    group_id = fields.Many2one(
        comodel_name='education.group', required=True, ondelete='cascade')
    session_number = fields.Integer()
    dayofweek = fields.Selection(
        selection='_get_selection_dayofweek', string='Day of Week',
        required=True, index=True, default=default_dayofweek)
    hour_from = fields.Float(string='Work from', required=True, index=True)
    hour_to = fields.Float(string='Work to', required=True)
    recess = fields.Boolean(string='Recess')

    _sql_constraints = [
        ('unique_session', 'unique(group_id,session_number,dayofweek)',
         'Session number unique per day of week and group!'),
    ]
