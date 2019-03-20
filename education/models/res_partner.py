# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    education_code = fields.Char(string='Education Code', copy=False)

    _sql_constraints = [
        ('education_code_uniq', 'unique(education_code)',
         'Education code must be unique!'),
    ]
