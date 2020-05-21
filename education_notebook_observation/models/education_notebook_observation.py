# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _


class EducationNotebookObservation(models.Model):
    _name = "education.notebook.observation"
    _description = "Education notebook observation"
    _order = 'observ_date, e_notebook_line_id, teacher_id, student_id'

    @api.depends('observations')
    def _compute_state(self):
        for observation in self:
            if observation.observations:
                observation.state = 'included'
            else:
                observation.state = 'pending'

    observ_date = fields.Date(
        string='Date')
    e_notebook_line_id = fields.Many2one(
        string='Education notebook line',
        comodel_name="education.notebook.line")
    teacher_id = fields.Many2one(
        string='Teacher', comodel_name='hr.employee',
        related='e_notebook_line_id.teacher_id', store=True)
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        domain=[('educational_category', '=', 'student')])
    calendar_event_id = fields.Many2one(
        string='Calendar event', comodel_name='calendar.event')
    observations = fields.Text(
        string='Observations')
    state = fields.Selection(
        selection=[('pending', _('Pending')),
                   ('included', _('Included')), ],
        default='pending', track_visibility='onchange',
        compute='_compute_state', store=True)
