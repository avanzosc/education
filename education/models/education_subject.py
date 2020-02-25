# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval
from .education_subject_type import SUBJECT_TYPE


class EducationSubject(models.Model):
    _name = 'education.subject'
    _inherit = 'education.data'
    _description = 'Education Subject'

    min_description = fields.Char(
        string='Min. Description')
    type_id = fields.Many2one(
        comodel_name='education.subject.type', string='Type')
    subject_type = fields.Selection(
        selection=SUBJECT_TYPE, string='Subject Type', related='type_id.type',
        store=True)
    level_field_ids = fields.One2many(
        comodel_name='education.level.field.subject',
        inverse_name='subject_id', string='Fields by Level')
    level_course_ids = fields.One2many(
        comodel_name='education.level.course.subject',
        inverse_name='subject_id', string='Courses by Level')
    level_ids = fields.Many2many(
        comodel_name='education.level', string='Levels',
        compute='_compute_level_ids', store=True,
        relation='edu_subject_level')
    field_ids = fields.Many2many(
        comodel_name='education.field', string='Study Fields',
        compute='_compute_field_ids', store=True,
        relation='edu_subject_field')
    course_ids = fields.Many2many(
        comodel_name='education.course', string='Courses',
        compute='_compute_course_ids', store=True,
        relation='edu_subject_course')

    @api.depends('level_field_ids', 'level_field_ids.field_id')
    def _compute_field_ids(self):
        for record in self:
            record.field_ids = record.with_context(active_test=False).mapped(
                'level_field_ids.field_id')

    @api.depends('level_field_ids', 'level_field_ids.level_id',
                 'level_course_ids', 'level_course_ids.level_id')
    def _compute_level_ids(self):
        for record in self:
            record.level_ids = (
                record.with_context(active_test=False).mapped(
                    'level_field_ids.level_id') |
                record.with_context(active_test=False).mapped(
                    'level_course_ids.level_id'))

    @api.depends('level_course_ids', 'level_course_ids.course_id')
    def _compute_course_ids(self):
        for record in self:
            record.course_ids = record.with_context(active_test=False).mapped(
                'level_course_ids.course_id')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]

    @api.multi
    def button_open_subject_center(self):
        self.ensure_one()
        action = self.env.ref('education.action_education_subject_center')
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [('subject_id', 'in', self.ids)],
            safe_eval(action.domain or '[]')
        ])
        context = safe_eval(action.context or '{}')
        context.update({
            'default_subject_id': self.id,
            'default_name': self.description,
        })
        action_dict.update({
            'domain': domain,
            'context': context,
        })
        return action_dict
