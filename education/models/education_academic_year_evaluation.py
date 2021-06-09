# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationAcademicYearEvaluation(models.Model):
    _name = 'education.academic_year.evaluation'
    _description = 'Evaluations for an academic year'
    _order = 'academic_year_id,sequence'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer()
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        ondelete='cascade', required=True, index=True)
    date_start = fields.Date(string='Date Start', required=True)
    date_end = fields.Date(string='Date End', required=True)
    current = fields.Boolean(
        string="Current Evaluation",
        compute="_compute_current_evaluation",
        search="_search_current_evaluation")

    @api.multi
    def _compute_current_evaluation(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.current = (record.date_start <= today <= record.date_end)

    @api.multi
    def _search_current_evaluation(self, operator, value):
        today = fields.Date.context_today(self)
        evaluations = self.search(
            [('date_start', '<=', today),
             ('date_end', '>=', today),
             ('academic_year_id.current', '=', value)])
        if operator == '=' and value:
            return [('id', 'in', evaluations.ids)]
        else:
            return [('id', 'not in', evaluations.ids)]

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

    def copy_data(self, default=None):
        name = _("{} (copy)").format(self.name)
        default = dict(default or {}, name=name)
        return super(EducationAcademicYearEvaluation, self).copy_data(default)
