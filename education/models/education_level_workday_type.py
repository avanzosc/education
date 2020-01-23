# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationLevelWorkdayType(models.Model):
    _name = 'education.level.workday_type'
    _description = 'Education Level and Workday Type Relation'
    _order = 'academic_year_id'

    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        required=True, ondelete='cascade')
    workday_type_id = fields.Many2one(
        comodel_name='education.workday_type', string='Workday Type')
    level_id = fields.Many2one(
        comodel_name='education.level', string='Education Level')
    dedicated_working_day = fields.Char(string='Dedicated Working Day')
    school_working_day = fields.Char(string='School Working Day')
