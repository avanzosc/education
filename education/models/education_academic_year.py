# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationAcademicYear(models.Model):
    _name = 'education.academic_year'
    _description = 'Academic Year'
    _order = 'name DESC'

    name = fields.Char(string='Academic Year', required=True)
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    evaluation_ids = fields.One2many(
        comodel_name='education.academic_year.evaluation',
        string='Evaluations', inverse_name='academic_year_id')
    active = fields.Boolean(string='Active', default=True)
    current = fields.Boolean(
        string="Current Academic Year",
        compute="_compute_current_academic_year",
        search="_search_current_academic_year")

    @api.multi
    def _compute_current_academic_year(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.current = (record.date_start <= today <= record.date_end)

    @api.multi
    def _search_current_academic_year(self, operator, value):
        today = fields.Date.context_today(self)
        years = self.search(
            [('date_start', '<=', today),
             ('date_end', '>=', today)])
        if operator == '=' and value:
            return [('id', 'in', years.ids)]
        else:
            return [('id', 'not in', years.ids)]

    @api.constrains('name')
    def _check_education_code(self):
        code_length = 9
        for record in self:
            if not len(record.name) == code_length:
                raise ValidationError(
                    _('Academic year must be {} digits long!').format(
                        code_length))

    @api.constrains('date_start', 'date_end')
    def _check_date_end_after_date_start(self):
        for record in self.filtered(lambda r: r.date_start and r.date_end):
            if not record.date_end > record.date_start:
                raise ValidationError(
                    _('End date must be after start date.'))
            if (record.mapped('evaluation_ids.date_start') and
                    record.date_start > min(
                    record.mapped('evaluation_ids.date_start'))):
                raise ValidationError(
                    _('Start date must be before evaluations start dates.'))
            if (record.mapped('evaluation_ids.date_end') and
                    record.date_end < max(
                    record.mapped('evaluation_ids.date_end'))):
                raise ValidationError(
                    _('End date must be after evaluations end dates.'))

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Academic year must be unique!'),
    ]

    @api.multi
    def write(self, vals):
        res = super(EducationAcademicYear, self).write(vals) if vals else True
        if 'active' in vals:
            # archiving/unarchiving a academic year does it on its groups, too
            group_obj = self.env['education.group'].with_context(
                active_test=False)
            groups = group_obj.search([('academic_year_id', 'in', self.ids)])
            groups.write({'active': vals['active']})
        return res
