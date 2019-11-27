# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResLang(models.Model):
    _inherit = 'res.lang'

    edu_lang_id = fields.Many2one(
        comodel_name='education.language', string='Education Language',
        copy=False)
    education_code = fields.Char(
        string='Education Code', related='edu_lang_id.education_code',
        store=True, readonly=True)

    _sql_constraints = [
        ('education_lang_unique', 'unique(edu_lang_id)',
         'Education lang must be unique!'),
    ]
