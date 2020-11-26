# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

EXAM_TYPE = [
    ("control", "Control exam"),
    ("evaluation", "Evaluation exam"),
    ("global", "Global exam"),
    ("project", "Project"),
    ("secondchance", "Second-chance"),
]


class EducationExamType(models.Model):
    _name = "education.exam.type"
    _description = "Exam Type"

    name = fields.Char(string="Name", required=True, translate=True)
    e_type = fields.Selection(
        selection=EXAM_TYPE, string="Exam Type", default="control",
        required=True)
    retake_type_id = fields.Many2one(
        comodel_name="education.exam.type", string="Retake Exam Type")
