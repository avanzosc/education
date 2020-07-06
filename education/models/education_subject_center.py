# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from .education_subject_type import SUBJECT_TYPE


class EducationSubjectCenter(models.Model):
    _name = "education.subject.center"
    _description = "Subject by Center, Level and Course"
    _rec_name = "subject_id"
    _order = "center_id,level_id,course_id,subject_id"

    subject_id = fields.Many2one(
        comodel_name="education.subject", string="Education Subject",
        required=True, ondelete="cascade")
    level_id = fields.Many2one(
        comodel_name="education.level", string="Education Level",
        required=True, ondelete="cascade")
    course_id = fields.Many2one(
        comodel_name="education.course", string="Course",
        required=True, ondelete="cascade")
    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        required=True, ondelete="cascade")
    group_type_id = fields.Many2one(
        comodel_name="education.group_type", string="Educational Group Type")
    name_ids = fields.One2many(
        comodel_name="education.subject.center.name",
        string="Name by Language", inverse_name="subject_center_id")
    subject_type = fields.Selection(
        selection=SUBJECT_TYPE, string="Subject Type")

    _sql_constraints = [
        ("subject_center_unique",
         "unique(subject_id,course_id,level_id,center_id)",
         "Subject must be unique per subject, course, level and center!"),
    ]

    @api.multi
    @api.onchange("subject_id")
    def _onchange_subject(self):
        self.ensure_one()
        self.subject_type = self.subject_id.subject_type
