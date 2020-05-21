# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationSchedule(models.Model):
    _name = 'education.schedule'
    _description = 'Class Schedule'

    @api.model
    def _get_selection_task_type_type(self):
        return self.env['education.task_type'].fields_get(
            allfields=['type'])['type']['selection']

    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center', required=True)
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        required=True)
    teacher_id = fields.Many2one(
        comodel_name='hr.employee', string='Teacher', required=True)
    task_type_id = fields.Many2one(
        comodel_name='education.task_type', string='Task Type', required=True)
    task_type_type = fields.Selection(
        selection='_get_selection_task_type_type', string='Task Type Type',
        related='task_type_id.type', store=True)
    resource_calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        related='teacher_id.resource_calendar_id', store=True)
    attendance_id = fields.Many2one(
        comodel_name='resource.calendar.attendance',
        domain="[('calendar_id', '=', resource_calendar_id)]")
    timetable_ids = fields.One2many(
        comodel_name='education.schedule.timetable', string='Timetable',
        inverse_name='schedule_id', copy=True)
    session_number = fields.Integer()
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
        column2='group_id')
    student_ids = fields.Many2many(
        comodel_name='res.partner', relation='edu_schedule_student',
        column1='schedule_id', column2='student_id',
        compute='_compute_student_ids', string='Students', store=True)
    student_count = fields.Integer(
        string='Student Number', compute='_compute_student_ids', store=True)

    @api.depends('group_ids', 'group_ids.student_ids')
    def _compute_student_ids(self):
        for schedule in self:
            schedule.student_ids = schedule.mapped(
                'group_ids.student_ids')
            schedule.student_count = len(schedule.student_ids)

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            description = (record.subject_id.description or
                           record.task_type_id.description)
            result.append((record.id, '{} [{}]'.format(
                description, record.teacher_id.name)))
        return result

    @api.multi
    def button_open_students(self):
        action = self.env.ref('base.action_partner_form')
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [('id', 'in', self.mapped('student_ids').ids)],
            safe_eval(action.domain or '[]')
        ])
        context = safe_eval(action.context or '[]')
        context.pop('search_default_customer')
        action_dict.update({
            'display_name': _('Students'),
            'domain': domain,
            'context': context,
        })
        return action_dict


class EducationScheduleTimetable(models.Model):
    _name = 'education.schedule.timetable'
    _description = 'Class Schedule Timetable'
    _order = 'dayofweek,session_number'

    @api.model
    def _get_selection_dayofweek(self):
        return self.env['resource.calendar.attendance'].fields_get(
            allfields=['dayofweek'])['dayofweek']['selection']

    def default_dayofweek(self):
        default_dict = self.env['resource.calendar.attendance'].default_get([
            'dayofweek'])
        return default_dict.get('dayofweek')

    schedule_id = fields.Many2one(
        comodel_name='education.schedule', string='Class Schedule',
        required=True, ondelete='cascade')
    dayofweek = fields.Selection(
        selection='_get_selection_dayofweek', string='Day of Week',
        required=True, index=True, default=default_dayofweek)
    hour_from = fields.Float(string='Work from', required=True, index=True)
    hour_to = fields.Float(string='Work to', required=True)
    session_number = fields.Integer()
    subject_name = fields.Char(string="Subject Name", copy=False)
    teacher_id = fields.Many2one(
        comodel_name='hr.employee', string='Teacher', copy=False)


class EducationScheduleGroup(models.Model):
    _name = 'education.schedule.group'
    _description = 'Class Schedule Group'

    schedule_id = fields.Many2one(
        comodel_name='education.schedule', string='Class Schedule',
        required=True, ondelete='cascade')
    group_id = fields.Many2one(
        comodel_name='education.group', string='Group', required=True,
        ondelete='cascade')
    group_type_id = fields.Many2one(
        comodel_name='education.group_type', string='Group Type',
        related='group_id.group_type_id')
    group_student_count = fields.Integer(
        related='group_id.student_count')
    parent_group_id = fields.Many2one(
        comodel_name='education.group', string='Parent Group', required=True,
        ondelete='cascade')
    parent_group_type_id = fields.Many2one(
        comodel_name='education.group_type', string='Parent Group Type',
        related='parent_group_id.group_type_id')
    parent_group_student_count = fields.Integer(
        related='parent_group_id.student_count')
    session_number = fields.Integer()
    student_count = fields.Integer()
    group_alias = fields.Char(string='Alias')
