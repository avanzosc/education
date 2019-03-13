# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationCourse(models.Model):
    _name = 'education.course'
    _inherit = 'education.data'
    _description = 'Course'

    level_id = fields.Many2one(
        comodel_name='education.level', string='Level', required=True,
        ondelete='cascade')
    field_id = fields.Many2one(
        comodel_name='education.field', string='Study Field')
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Plan')
    shift_id = fields.Many2one(
        comodel_name='education.shift', string='Shift')
    level_subject_ids = fields.One2many(
        comodel_name='education.level.course.subject',
        inverse_name='course_id', string='Subjects by Level')

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 4
        for record in self:
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code,level_id,field_id)',
         'Education code must be unique per level and field!'),
    ]
