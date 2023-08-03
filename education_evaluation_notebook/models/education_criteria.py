# Copyright 2023 Leire Martinez de Santos - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
        relation="specific_comp_subject_criteria_rel",
        column1="criteria_id", column2="specific_comp_id",
        related="competence_specific_id.subject_ids",
        store=True
    )
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
        domain="["
               "('id', 'in', specific_comp_subject_ids),"
               "('course_ids', 'in', course_ids),"
               "]")

    @api.onchange('course_ids')
    def onchange_course_ids(self):
        for record in self:
            if not record.course_ids:
                subject_ids = record.specific_comp_subject_ids
            else:
                subject_ids = self.env['education.subject'].search([
                    ('id', 'in', record.specific_comp_subject_ids.ids),
                    ('course_ids', 'in', record.course_ids.ids),
                ])
            record.subject_ids = subject_ids
