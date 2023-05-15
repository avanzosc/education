# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationCompetenceType(models.Model):
    _name = "education.competence.type"
    _description = "Competence Type"

    name = fields.Char(string="Name")
    description = fields.Char(string="Competence type description")
    competence_profile_id = fields.Many2one(
        comodel_name="education.competence.profile",
        string="Competence profile")
    education_level_ids = fields.Many2many(
        comodel_name="education.level",
        string="Education Levels")
