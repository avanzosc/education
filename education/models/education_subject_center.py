# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationSubjectCenter(models.Model):
    _name = "education.subject.center"
    _description = "Subject Name by Center, Language and Course"

    name = fields.Char(string="Subject Name", required=True)
    subject_id = fields.Many2one(
        comodel_name="education.subject", string="Education Subject",
        required=True, ondelete="cascade")
    course_id = fields.Many2one(
        comodel_name="education.course", string="Course",
        required=True, ondelete="cascade")
    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        required=True, ondelete="cascade")
    lang_id = fields.Many2one(
        comodel_name="education.language", string="Language",
        required=True, ondelete="cascade")

    _sql_constraints = [
        ("name_unique", "unique(subject_id,course_id,center_id,lang_id)",
         "Subject must be unique per subject, course, language and center!"),
    ]
