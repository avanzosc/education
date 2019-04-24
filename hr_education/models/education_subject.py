# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationSubject(models.Model):
    _inherit = 'education.subject'

    level_id = fields.Many2one(
        comodel_name='education.level', string='Level',
        compute='_compute_level_field')
    field_id = fields.Many2one(
        comodel_name='education.field', string='Study Field',
        compute='_compute_level_field')
    course_ids = fields.Many2many(
        comodel_name='education.course', string='Courses',
        compute='_compute_course_ids')

    @api.depends('level_field_ids', 'level_field_ids.level_id',
                 'level_field_ids.field_id')
    def _compute_level_field(self):
        for record in self:
            record.level_id = record.level_field_ids[:1].level_id
            record.field_id = record.level_field_ids[:1].field_id

    @api.depends('level_course_ids', 'level_course_ids.course_id')
    def _compute_course_ids(self):
        for record in self:
            record.course_ids = record.mapped('level_course_ids.course_id')
