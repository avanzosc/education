# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationSubject(models.Model):
    _name = 'education.subject'
    _inherit = 'education.data'
    _description = 'Education Subject'

    min_description = fields.Char(
        string='Min. Description')
    type = fields.Char(string='Type')
    type_id = fields.Many2one(
        comodel_name='education.subject.type', string='Type')
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
            record.field_ids = record.mapped('level_field_ids.field_id')

    @api.depends('level_field_ids', 'level_field_ids.level_id',
                 'level_course_ids', 'level_course_ids.level_id')
    def _compute_level_ids(self):
        for record in self:
            record.level_ids = (record.mapped('level_field_ids.level_id') |
                                record.mapped('level_course_ids.level_id'))

    @api.depends('level_course_ids', 'level_course_ids.course_id')
    def _compute_course_ids(self):
        for record in self:
            record.course_ids = record.mapped('level_course_ids.course_id')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]


class EducationSubjectType(models.Model):
    _name = 'education.subject.type'
    _inherit = 'education.data'

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
