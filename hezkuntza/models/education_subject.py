# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

TIPO_ASIGNATURA_INDICES = [
    (0, False),
    ('0001', 'Obligatoria'),
    ('0002', 'Religión (opcional)'),
    ('0004', 'Común'),
    ('0005', 'Modalidad (BACH)'),
    ('0006', 'Optativa'),
    ('0007', 'Optativa (ESO)'),
    ('0008', 'Libre elección'),
    ('0009', 'Específica'),
    ('0010', 'Modalidad'),
    ('0014', 'Optativa (BACH)'),
    ('0015', 'Obligatoria (ESO)'),
    ('0016', 'Obligatoria (ESO)'),
    ('0017', 'Obligatoria (ESO)'),
]


class EducationSubject(models.Model):
    _inherit = 'education.subject'

    min_description_eu = fields.Char(
        string='Basque Min. Description')

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 8
        for record in self:
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))
