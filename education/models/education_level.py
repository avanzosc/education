# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationLevel(models.Model):
    _name = 'education.level'
    _inherit = 'education.data'
    _description = 'Education Level'

    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Plan', required=True,
        ondelete='cascade')
    task_type_ids = fields.Many2many(
        comodel_name='education.task_type', string='Task Types',
        relation='rel_education_level_task_type',
        column1='level_id', column2='task_type_id')
    academic_year_workday_type_id = fields.One2many(
        comodel_name='education.level.workday_type', inverse_name='level_id',
        string='Workday Type per Academic Year')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code,plan_id)',
         'Education code must be unique per plan!'),
    ]
