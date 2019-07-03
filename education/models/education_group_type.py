# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationGroupType(models.Model):
    _name = 'education.group_type'
    _inherit = 'education.data'
    _description = 'Educational Group Type'

    type = fields.Selection(
        selection=[('official', 'Official'),
                   ('class', 'Class'),
                   ('other', 'Other')], string='Type',
        required=True, default='other')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
