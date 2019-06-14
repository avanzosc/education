# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationSchedule(models.Model):
    _name = 'education.schedule'
    _description = 'Class Schedule'
    _order = 'dayofweek,session_number'

    @api.model
    def _get_selection_dayofweek(self):
        return self.env['resource.calendar.attendance'].fields_get(
            allfields=['dayofweek'])['dayofweek']['selection']

    def default_dayofweek(self):
        default_dict = self.env['resource.calendar.attendance'].default_get([
            'dayofweek'])
        return default_dict.get('dayofweek')

    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center')
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year')
    teacher_id = fields.Many2one(
        comodel_name='hr.employee', string='Teacher')
    task_type_id = fields.Many2one(
        comodel_name='education.task_type', string='Task Type')
    session_number = fields.Integer()
    dayofweek = fields.Selection(
        selection='_get_selection_dayofweek', string='Day of Week',
        required=True, index=True, default=default_dayofweek)
    hour_from = fields.Float(string='Work from', required=True, index=True)
    hour_to = fields.Float(string='Work to', required=True)
    classroom_id = fields.Many2one(
        comodel_name='education.classroom', string='Classroom',
        domain="[('center_id', '=', center_id)]")
    subject_id = fields.Many2one(
        comodel_name='education.subject', string='Education Subject')
    subject_type = fields.Char()
    language_id = fields.Many2one(
        comodel_name='education.language', string='Language')
    activity_type_id = fields.Many2one(
        comodel_name='education.activity_type', string='Other Activity')
    level_id = fields.Many2one(
        comodel_name='education.level', string='Level')
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Education Plan')
    group_ids = fields.Many2many(
        comodel_name='education.group', string='Education Groups',
        relation='edu_schedule_group', column1='schedule_id',
        column2='group_id',
        domain="[('academic_year_id', '=', academic_year_id),"
               "('center_id', '=', center_id)]")
    schedule_group_ids = fields.One2many(
        comodel_name='education.schedule.group', inverse_name='schedule_id',
        string='Groups')
    student_ids = fields.Many2many(
        comodel_name='res.partner', relation='edu_schedule_student',
        column1='schedule_id', column2='student_id',
        compute='_compute_student_ids')

    @api.depends('group_ids', 'group_ids.student_ids')
    def _compute_student_ids(self):
        for schedule in self:
            schedule.student_ids = schedule.mapped(
                'group_ids.student_ids')


class EducationScheduleGroup(models.Model):
    _name = 'education.schedule.group'
    _description = 'Class Schedule Group'

    schedule_id = fields.Many2one(
        comodel_name='education.schedule', string='Schedule')
    group_id = fields.Many2one(
        comodel_name='education.group', string='Group', required=True)
    group_type_id = fields.Many2one(
        comodel_name='education.group_type', string='Group Type',
        related='group_id.group_type_id')
    group_student_count = fields.Integer(
        related='parent_group_id.student_count')
    parent_group_id = fields.Many2one(
        comodel_name='education.group', string='Parent Group', required=True)
    parent_group_type_id = fields.Many2one(
        comodel_name='education.group_type', string='Parent Group Type',
        related='parent_group_id.group_type_id')
    parent_group_student_count = fields.Integer(
        related='parent_group_id.student_count')
    session_number = fields.Integer()
    student_count = fields.Integer()
    group_alias = fields.Char(string='Alias')
