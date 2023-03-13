# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationGroup(models.Model):
    _name = 'education.group'
    _inherit = ['education.data', 'mail.thread', 'mail.activity.mixin']
    _description = 'Education Group'
    _rec_name = 'description'
    _order = 'academic_year_id, education_code'

    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        required=True, index=True)
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        required=True, index=True)
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Plan', required=True)
    level_id = fields.Many2one(
        comodel_name='education.level', string='Education Level',
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
               "('field_id', '=', field_id), ('shift_id', '=', shift_id)]",
        index=True)
    model_id = fields.Many2one(
        comodel_name='education.model', string='Educational Model')
    group_type_id = fields.Many2one(
        comodel_name='education.group_type', string='Educational Group Type',
        index=True)
    calendar_id = fields.Many2one(
        comodel_name='resource.calendar', string='Calendar',
        domain="[('center_id', '=', center_id)]")
    section_id = fields.Many2one(
        comodel_name='education.section', string='Section')
    comments = fields.Text(string='Comments')
    teacher_ids = fields.One2many(
        comodel_name='education.group.teacher',
        inverse_name='group_id', string='Teachers', copy=False)
    session_ids = fields.One2many(
        comodel_name='education.group.session', inverse_name='group_id',
        string='Sessions', copy=True)
    calendar_session_ids = fields.Many2many(
        comodel_name='resource.calendar.attendance',
        relation="education_group_attendance_rel", column1="group_id",
        column2="attendance_id", compute="_compute_calendar_session")
    student_ids = fields.Many2many(
        comodel_name='res.partner', relation='edu_group_student',
        column1='group_id', column2='student_id', string='Students',
        copy=False)
    student_count = fields.Integer(
        string='Student Number', compute='_compute_student_count', store=True,
        group_operator="avg")
    parent_id = fields.Many2one(
        comodel_name='education.group', string='Parent Group',
        domain="[('academic_year_id', '=', academic_year_id),"
               "('center_id', '=', center_id),"
               "('course_id', '=', course_id),"
               "('group_type_id.type', '=', 'official')]", copy=False,
        index=True)
    schedule_ids = fields.Many2many(
        comodel_name='education.schedule', string='Class Schedule',
        relation='edu_schedule_group', column2='schedule_id',
        column1='group_id', readonly=True, copy=False)
    schedule_count = fields.Integer(
        compute='_compute_schedule_count', string='Schedule Number')
    timetable_ids = fields.One2many(
        comodel_name="education.group.teacher.timetable.report",
        compute="_compute_timetable_ids")

    _sql_constraints = [
        ('education_code_unique',
         'unique(education_code,center_id,academic_year_id)',
         'Education code must be unique per center and academic year!'),
    ]

    @api.constrains('parent_id')
    def _check_group_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive groups.'))

    @api.constrains("student_ids", "group_type_id")
    def _check_unique_official_group_per_year(self):
        for group in self.filtered(
                lambda g: g.group_type_id.type == "official"):
            for student in group.student_ids:
                groups = self.search([
                    ("student_ids", "in", student.ids),
                    ("group_type_id.type", "=", "official"),
                    ("academic_year_id", "=", group.academic_year_id.id),
                    ("id", "!=", group.id),
                ])
                if groups:
                    raise ValidationError(
                        _("{} is already in one official group").format(
                            student.display_name))

    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    @api.depends('schedule_ids')
    def _compute_schedule_count(self):
        for record in self:
            record.schedule_count = len(record.schedule_ids)

    @api.depends("calendar_id", "calendar_id.attendance_ids")
    def _compute_calendar_session(self):
        for record in self:
            record.calendar_session_ids = [
                (6, 0, record.calendar_id.attendance_ids.ids)]

    @api.multi
    def _compute_timetable_ids(self):
        timetable_obj = self.env["education.group.teacher.timetable.report"]
        for record in self:
            record.timetable_ids = timetable_obj.search([
                "|", ("group_id", "=", record.id),
                ("group_id.parent_id", "=", record.id)
            ])

    @api.multi
    def button_open_schedule(self):
        action = self.env.ref('education.action_education_schedule_from_group')
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [('id', 'in', self.mapped('schedule_ids').ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({
            'domain': domain,
        })
        return action_dict

    @api.multi
    def button_open_students(self):
        action = self.env.ref('education.res_partner_education_action')
        action_dict = self.open_students(action)
        return action_dict

    @api.multi
    def button_edit_students(self):
        if self.group_type_id.type != "official":
            raise UserError(
                _("You can only edit photos from official groups."))
        action = self.env.ref('education.res_partner_photo_education_action')
        action_dict = self.open_students(action)
        return action_dict

    def open_students(self, action):
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [('id', 'in', self.mapped('student_ids').ids)],
            safe_eval(action.domain or '[]')
        ])
        action_dict.update({
            'display_name': _('Students'),
            'domain': domain,
        })
        return action_dict

    @api.multi
    def _get_next_year_group(self, next_year):
        groups = self.env["education.group"]
        for group in self.filtered(
                lambda g: g.group_type_id.type == "official" and
                g.academic_year_id.current):
            next_group = self.search([
                ("education_code", "=", group.education_code),
                ("center_id", "=", group.center_id.id),
                ("academic_year_id", "=", next_year.id),
            ])
            if not next_group:
                next_group = group.copy(default={
                    'academic_year_id': next_year.id,
                    'education_code': group.education_code,
                })
            groups |= next_group
        return groups

    @api.multi
    def create_next_academic_year(self):
        next_groups = self.env["education.group"]
        for record in self.filtered(
                lambda g: g.group_type_id.type == "official" and
                g.academic_year_id.current):
            next_year = record.academic_year_id._get_next()
            if next_year:
                try:
                    next_groups |= record._get_next_year_group(next_year)
                except Exception:
                    pass
        return next_groups

    def get_report_file_name(self):
        return "{}-{}-{}".format(
            self.education_code, re.sub(r"[\W_]+", "", self.description),
            re.sub(r"[\W_]+", "", self.center_id.display_name))

    @api.multi
    def get_timetable_max_daily_hour(self):
        self.ensure_one()
        reports = self.timetable_ids.filtered(
            lambda r: r.academic_year_id.current)
        return max(reports.mapped("daily_hour")) if reports else False

    @api.multi
    def get_timetable_info(self, dayofweek, daily_hour):
        self.ensure_one()
        reports = self.timetable_ids.filtered(
            lambda r: r.academic_year_id.current)
        return reports.filtered(
            lambda r: r.dayofweek == str(dayofweek) and
            r.daily_hour == daily_hour)


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
    _order = 'group_id, dayofweek, session_number'

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
