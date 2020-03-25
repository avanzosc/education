# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationHomework(models.Model):
    _name = "education.homework"
    _description = "Education Homework"

    name = fields.Char(string="Description", required=True)
    date = fields.Date(string="Deadline", required=True)
    schedule_id = fields.Many2one(
        comodel_name="education.schedule", string="Class Schedule")
    html_link = fields.Char(string="HTML link")
