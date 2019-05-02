# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationGroup(models.Model):
    _name = 'education.group'
    _inherit = 'education.data'
    _description = 'Education Group'

    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        domain=[('education_code', '!=', False)])
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Plan')
    level_id = fields.Many2one(
        comodel_name='education.level', string='Level')
    field_id = fields.Many2one(
        comodel_name='education.field', string='Study Field')
    classroom_id = fields.Many2one(
        comodel_name='education.classroom', string='Classroom')

    _sql_constraints = [
        ('education_code_unique',
         'unique(education_code,center_id,academic_year_id)',
         'Education code must be unique per center and academic year!'),
    ]
