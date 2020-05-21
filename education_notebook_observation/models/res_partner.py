# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    student_notebook_observation_ids = fields.One2many(
        string='Notebook observations', inverse_name='student_id',
        comodel_name='education.notebook.observation')
