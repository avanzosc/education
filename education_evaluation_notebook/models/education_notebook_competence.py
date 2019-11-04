# Copyright (c) 2019 Adrian Revilla <adrianrevilla@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class educationCompetence(models.Model):
    _name = 'education.competence'
    _description = 'Educational competences'

    name = fields.Char(string='Name', required=True)
    eval_mode = fields.Selection([
        ('numeric', 'Numeric'),
        ('behaviour', 'Behaviour'),
        ('both', 'Both')],
        string='Evaluation mode', default='numeric', required=True
    )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Competence] {}'.format(
                 record.name)))
        return result