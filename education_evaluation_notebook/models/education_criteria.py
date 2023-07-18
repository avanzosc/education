# Copyright 2023 Leire Martinez de Santos - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationCriteria(models.Model):
    _name = "education.criteria"
    _description = "Education Criteria"

    name = fields.Char(string="Code")
    description = fields.Char(string="Description")
    competence_specific_id = fields.Many2one(
        comodel_name="education.competence.specific",
        string="Specific Competence")
    level_ids = fields.Many2many(
        comodel_name="education.level",
        string="Education Levels", related="competence_specific_id.level_ids")
    specific_comp_subject_ids = fields.Many2many(
        comodel_name="education.subject",
        string="Education subjects related",
        related="competence_specific_id.subject_ids")
    school_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Schools",
        related="competence_specific_id.school_ids")
    course_ids = fields.Many2many(
        comodel_name="education.course",
        string="Education Courses",
        domain="[('level_id', 'in', level_ids)]")
    subject_ids = fields.Many2many(
        comodel_name="education.subject",
        string="Education Subjects",
        domain="[('id', 'in', specific_comp_subject_ids)]")
