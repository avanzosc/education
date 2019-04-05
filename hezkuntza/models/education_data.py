# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationData(models.AbstractModel):
    _inherit = 'education.data'

    description_eu = fields.Text(string='Basque Description')
    short_description_eu = fields.Char(string='Basque Short Description')
