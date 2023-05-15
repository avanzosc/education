# Copyright 2023 Leire Martinez de Santos - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationCompetenceProfile(models.Model):
    _name = "education.competence.profile"
    _description = "Competence Profile"

    name = fields.Char(string="Name")
    description = fields.Char(string="Competence profile description")
