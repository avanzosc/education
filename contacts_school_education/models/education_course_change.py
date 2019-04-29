# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationCourseChange(models.Model):
    _name = 'education.course.change'
    _description = 'Course Change'

    @api.model
    def _get_selection_gender(self):
        return self.env['res.partner'].fields_get(
            allfields=['gender'])['gender']['selection']

    school_id = fields.Many2one(
        comodel_name='res.partner', string='School', required=True,
        domain=[('educational_category', '=', 'school')])
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course', required=True)
    next_school_id = fields.Many2one(
        comodel_name='res.partner', string='Next School', required=True,
        domain=[('educational_category', '=', 'school')])
    next_course_id = fields.Many2one(
        comodel_name='education.course', string='Next Course', required=True)
    gender = fields.Selection(
        string='Gender', selection=_get_selection_gender)
