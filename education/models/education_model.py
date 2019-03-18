# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class EducationModel(models.Model):
    _name = 'education.model'
    _inherit = 'education.data'
    _description = 'Educational Model'

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
