# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationSection(models.Model):
    _name = 'education.section'
    _description = 'Education Section'

    name = fields.Char(string='Name')
