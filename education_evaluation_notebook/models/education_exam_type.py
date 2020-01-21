# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationExamType(models.Model):
    _name = "education.exam.type"
    _description = "Exam Type"

    name = fields.Char(string="Name", required=True, translate=True)
    e_type = fields.Selection(selection=[
        ("control", "Control exam"),
        ("evaluation", "Evaluation exam"),
        ("global", "Global exam"),
        ("project", "Project"),
        ("secondchance", "Second-chance")],
        string="Exam Type", default="control", required=True)
