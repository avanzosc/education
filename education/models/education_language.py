# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationLanguage(models.Model):
    _name = 'education.language'
    _inherit = 'education.data'
    _description = 'Language'

    lang_id = fields.Many2one(
        comodel_name='res.lang', string='Language', compute='_compute_lang_id',
        inverse='_inverse_lang_id')

    @api.multi
    def _compute_lang_id(self):
        language_obj = self.env['res.lang']
        for lang in self:
            lang.lang_id = language_obj.search([
                ('edu_lang_id', '=', lang.id)])[:1]

    @api.multi
    def _inverse_lang_id(self):
        language_obj = self.env['res.lang']
        for lang in self:
            languages = language_obj.search([
                ('edu_lang_id', '=', lang.id),
                ('id', '!=', lang.lang_id.id),
            ])
            languages.write({
                'edu_lang_id': False,
            })
            lang.lang_id.write({
                'edu_lang_id': lang.id,
            })

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]
