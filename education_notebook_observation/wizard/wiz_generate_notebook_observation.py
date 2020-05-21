# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class WizGenerateNotebookObservation(models.TransientModel):
    _name = "wiz.generate.notebook.observation"
    _description = "Wizard for generate notebook observations"

    line_ids = fields.One2many(
        string='Lines', comodel_name='wiz.generate.notebook.observation.line',
        inverse_name='wiz_id')

    @api.model
    def default_get(self, fields):
        result = super(
            WizGenerateNotebookObservation, self).default_get(fields)
        if self._context.get('active_id'):
            calendar = self.env['calendar.event'].browse(
                self._context['active_id'])
            observations = []
            observation_ids = calendar.calendar_event_notebook_observation_ids
            school_year_id = calendar.supervised_year_id.school_year_id
            cond = [('academic_year_id', '=', school_year_id.id),
                    ('student_id', '=', calendar.student_id.id),
                    ('n_line_id.competence_id', '!=', False)]
            records = self.env['education.record'].search(cond)
            if records:
                lines = records.mapped('n_line_id').filtered(
                    lambda x: x.competence_id.evaluation_check)
                for line in lines:
                    found = observation_ids.filtered(
                        lambda x: x.e_notebook_line_id == line.id)
                    if not found:
                        vals = {
                            'education_notebook_line_id': line.id,
                            'teacher_id': line.teacher_id.id}
                        observations.append((0, 0, vals))
            result.update({'line_ids': observations})
        return result

    @api.multi
    def button_generate_notebook_observations(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', []) or []
        calendar = self.env['calendar.event'].browse(active_id)
        if calendar and self.line_ids:
            notebook_lines = self.line_ids.mapped('education_notebook_line_id')
            calendar.generate_notebook_observations(notebook_lines)
        return {'type': 'ir.actions.act_window_close'}


class WizGenerateNotebookObservationLine(models.TransientModel):
    _name = "wiz.generate.notebook.observation.line"
    _description = "lines of wizard for generate notebook observations"

    wiz_id = fields.Many2one(
        string='Wizard', comodel_name='wiz.generate.notebook.observation')
    education_notebook_line_id = fields.Many2one(
        string='Education Notebook Line',
        comodel_name='education.notebook.line')
    teacher_id = fields.Many2one(
        string='Teacher', comodel_name='hr.employee')
