# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class EducationDesignationLevel(models.Model):
    _name = 'education.designation_level'
    _inherit = 'education.data'
    _description = 'Education Designation Level'

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
