# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationCourse(models.Model):
    _inherit = 'education.course'

    course_value = fields.Integer(string="Course Value to Export XML")

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 4
        for record in self:
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))
