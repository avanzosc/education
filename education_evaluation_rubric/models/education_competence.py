# Copyright 2022 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class EducationCompetence(models.Model):
    _inherit = 'education.competence'

    eval_mode = fields.Selection(selection_add=[('rubric', 'Rubric')])
