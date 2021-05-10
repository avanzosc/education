# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

HEZKUNTZA_LEVEL_CODE = [
    ("1120", "Elementary School"),
    ("2260", "Compulsory Secondary Education"),
    ("3270", "High School"),
    ("4310", "LOGSE - Medium Grade Vocational Training"),
    ("5320", "LOGSE - Higher Grade Vocational Training"),
    ("6310", "LOE - Medium Grade Vocational Training"),
    ("7320", "LOE - Higher Grade Vocational Training"),
    ("8550", "LOE - Basic Vocational Training"),
]


class EducationLevel(models.Model):
    _inherit = 'education.level'

    hezkuntza_level = fields.Selection(
        selection=HEZKUNTZA_LEVEL_CODE,
        string="Education Levels to Export XML")

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 4
        for record in self:
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))
