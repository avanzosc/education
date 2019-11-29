# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

SUBJECT_TYPE = [('optional', 'Optional'),
                ('compulsory', 'Compulsory'),
                ('free', 'Free Choice')]


class EducationSubjectType(models.Model):
    _name = 'education.subject.type'
    _inherit = 'education.data'
    _description = 'Education Subject Type'

    type = fields.Selection(
        selection=SUBJECT_TYPE,
        string='Type', default='optional', required=True)

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
