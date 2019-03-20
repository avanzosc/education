# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationTaskType(models.Model):
    _name = 'education.task_type'
    _inherit = 'education.data'
    _description = 'Education Task Type'

    type = fields.Char()
    tutoring = fields.Char()
    level = fields.Char()
    other_activities = fields.Char()
    level_ids = fields.Many2many(
        comodel_name='education.level', string='Levels',
        relation='rel_education_level_task_type',
        column1='task_type_id', column2='level_id')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
