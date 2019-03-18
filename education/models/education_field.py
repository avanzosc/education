# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationField(models.Model):
    _name = 'education.field'
    _inherit = 'education.data'
    _description = 'Education Field'

    level_subject_ids = fields.One2many(
        comodel_name='education.level.field.subject', inverse_name='field_id',
        string='Subjects by Levels')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
