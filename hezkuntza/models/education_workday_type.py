# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class EducationWorkdayType(models.Model):
    _name = 'education.workday_type'
    _inherit = 'education.data'
    _description = 'Education Type of Workday'

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 9
        for record in self:
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
