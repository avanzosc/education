# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationAcademicYearEvaluation(models.Model):
    _inherit = 'education.academic_year.evaluation'

    school_id = fields.Many2one(comodel_name='res.partner',
                                string='School', required=True)
    course_id = fields.Many2one(comodel_name='education.course',
                                string='Course', required=True)
