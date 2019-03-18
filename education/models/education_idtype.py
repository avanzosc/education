# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class EducationIdType(models.Model):
    _name = 'education.idtype'
    _inherit = 'education.data'
    _description = 'Education ID Type'

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
