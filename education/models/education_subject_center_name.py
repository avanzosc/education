# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationSubjectCenterName(models.Model):
    _name = "education.subject.center.name"
    _description = "Subject Name per Center and Language"

    subject_center_id = fields.Many2one(
        comodel_name="education.subject.center",
        string="Subject Center Relation", required=True, ondelete="cascade")
    name = fields.Char(string="Subject Name", required=True)
    lang_id = fields.Many2one(
        comodel_name="education.language", string="Language",
        required=True, ondelete="cascade")

    _sql_constraints = [
        ("center_name_unique", "unique(subject_center_id,lang_id)",
         "Subject name must be unique per language and center!"),
    ]
