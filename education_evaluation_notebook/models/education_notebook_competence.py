# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationCompetence(models.Model):
    _name = 'education.competence'
    _description = 'Education competence'

    name = fields.Char(string='Name', required=True)
    eval_mode = fields.Selection(selection=[
        ('numeric', 'Numeric'),
        ('behaviour', 'Behaviour'),
        ('both', 'Both')],
        string='Evaluation mode', default='numeric', required=True
    )
    evaluation_check = fields.Boolean(string='Master evaluation competence',
                                      default=False)
    global_check = fields.Boolean(string='Master global competence',
                                  default=False)
