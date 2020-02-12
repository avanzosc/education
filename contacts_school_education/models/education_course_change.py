# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationCourseChange(models.Model):
    _name = 'education.course.change'
    _description = 'Course Change'
    _order = 'school_id,course_id,next_school_id,next_course_id,gender'

    @api.model
    def _get_selection_gender(self):
        return self.env['res.partner'].fields_get(
            allfields=['gender'])['gender']['selection']

    school_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center', required=True,
        domain=[('educational_category', '=', 'school')])
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course', required=True)
    next_school_id = fields.Many2one(
        comodel_name='res.partner', string='Next Education Center',
        required=True, domain=[('educational_category', '=', 'school')],
        copy=False)
    next_course_id = fields.Many2one(
        comodel_name='education.course', string='Next Course', required=True,
        copy=False)
    gender = fields.Selection(
        string='Gender', selection=_get_selection_gender, copy=False)

    @api.constrains('course_id', 'next_course_id')
    def _check_different_course(self):
        for record in self:
            if record.course_id == record.next_course_id:
                raise ValidationError(_('Courses must be different.'))

    @api.constrains(
        'school_id', 'course_id', 'next_school_id', 'next_course_id', 'gender')
    def _check_course_change_unique(self):
        for record in self:
            results = self.search_count([
                ('school_id', '=', record.school_id.id),
                ('course_id', '=', record.course_id.id),
                ('next_school_id', '=', record.next_school_id.id),
                ('next_course_id', '=', record.next_course_id.id),
                ('gender', '=', record.gender),
                ('id', '!=', record.id),
            ])
            if results:
                raise ValidationError(
                    _("Duplicated course change!"))
