# Copyright 2023 Leire Martinez de Santos - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationCompetenceSpecific(models.Model):
    _name = "education.competence.specific"
    _description = "Education Competence Specific"

    name = fields.Char(string="Code")
    description = fields.Char(string="Description")
    level_ids = fields.Many2many(
        comodel_name="education.level",
        string="Education Levels")
    school_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Schools",
        domain="[('educational_category', '=', 'school')]")
    competence_type_ids = fields.Many2many(
        comodel_name="education.competence.type",
        string="Competence Types",
        relation="edu_comp_specific_type_rel",
        column1="comp_specific_id", column2="comp_type_id",
        domain="["
               "'|',"
               "('education_level_ids', 'in', level_ids),"
               "('education_level_ids', '=', False)]")
    subject_ids = fields.Many2many(
        comodel_name="education.subject",
        string="Education Subjects",
        domain="["
               "'|',"
               "('level_ids', 'in', level_ids),"
               "('level_ids', '=', False)]")
