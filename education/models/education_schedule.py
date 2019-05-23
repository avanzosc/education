# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationSchedule(models.Model):
    _name = 'education.schedule'
    _description = 'Class Schedule'
    _order = 'dayofweek,session_number'

    @api.model
    def _get_selection_dayofweek(self):
        return self.env['resource.calendar.attendance'].fields_get(
            allfields=['dayofweek'])['dayofweek']['selection']

    def default_dayofweek(self):
        default_dict = self.env['resource.calendar.attendance'].default_get([
            'dayofweek'])
        return default_dict.get('dayofweek')

    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center')
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year')
    teacher_id = fields.Many2one(
        comodel_name='hr.employee', string='Teacher')
    task_type_id = fields.Many2one(
        comodel_name='education.task_type', string='Task Type')
    session_number = fields.Integer()
    dayofweek = fields.Selection(
        selection='_get_selection_dayofweek', string='Day of Week',
        required=True, index=True, default=default_dayofweek)
    hour_from = fields.Float(string='Work from', required=True, index=True)
    hour_to = fields.Float(string='Work to', required=True)
    classroom_id = fields.Many2one(
        comodel_name='education.classroom', string='Classroom',
        domain="[('center_id', '=', center_id)]")
    subject_id = fields.Many2one(
        comodel_name='education.subject', string='Education Subject')
    subject_type = fields.Char()
    language_id = fields.Many2one(
        comodel_name='education.language', string='Language')
    activity_type_id = fields.Many2one(
        comodel_name='education.activity_type', string='Other Activity')
    level_id = fields.Many2one(
        comodel_name='education.level', string='Level')
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Education Plan')
