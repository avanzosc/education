# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationPosition(models.Model):
    _name = 'education.position'
    _inherit = 'education.data'
    _description = 'Education Position'
    _order = 'education_code,type'

    type = fields.Selection(
        selection=[('normal', 'Normal'),
                   ('other', 'Other')],
        string='Position Type', required=True, oldname='tipo')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code,type)',
         'Education code must be unique per type!'),
    ]
