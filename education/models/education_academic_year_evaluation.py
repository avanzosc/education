# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationAcademicYearEvaluation(models.Model):
    _name = 'education.academic_year.evaluation'
    _description = 'Evaluations for an academic year'

    name = fields.Char(string='Evaluation Name', required=True)
    sequence = fields.Integer()
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        ondelete='cascade', required=True)
    date_start = fields.Date(string='Date Start', required=True)
    date_end = fields.Date(string='Date End', required=True)

    @api.constrains('academic_year_id', 'date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if not record.date_end > record.date_start:
                raise ValidationError(
                    _('End date must be after start date.'))
            min_date_start = record.academic_year_id.date_start
            max_date_end = record.academic_year_id.date_end
            check_date_start = (
                (min_date_start and min_date_start > record.date_start) or
                (max_date_end and record.date_start > max_date_end))
            check_date_end = (
                (min_date_start and min_date_start > record.date_end) or
                (max_date_end and record.date_end > max_date_end))
            if check_date_start or check_date_end:
                raise ValidationError(
                    _('Evaluation dates must be between academic year dates.'))

    _sql_constraints = [
        ('name_unique', 'unique(name, academic_year_id)',
         'Evaluation name must be unique!'),
    ]
