# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationSubject(models.Model):
    _name = 'education.subject'
    _inherit = 'education.data'
    _description = 'Education Subject'

    min_description = fields.Char(
        string='Min. Description')
    type = fields.Char(string='Type')
    level_field_ids = fields.One2many(
        comodel_name='education.level.field.subject',
        inverse_name='subject_id', string='Fields by Level')
    level_course_ids = fields.One2many(
        comodel_name='education.level.course.subject',
        inverse_name='subject_id', string='Courses by Level')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
