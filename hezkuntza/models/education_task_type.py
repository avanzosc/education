# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

LECTIVA = {
    'L': 'lectiva',
    'N': 'no_lectiva',
}
REFUERZO = {
    1: 'si',
    2: 'no',
}


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

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 4
        for record in self:
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
