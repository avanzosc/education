# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationCompetenceType(models.Model):
    _name = "education.competence.type"
    _description = "Competence Type"

    name = fields.Char(string="Name")
