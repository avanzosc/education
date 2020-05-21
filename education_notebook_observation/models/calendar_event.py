# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    calendar_event_notebook_observation_ids = fields.One2many(
        string='Notebook observations', inverse_name='calendar_event_id',
        comodel_name='education.notebook.observation')

    def generate_notebook_observations(self, notebook_lines):
        observation_obj = self.env['education.notebook.observation']
        for line in notebook_lines:
            observation_obj.create(
                self._catch_notebook_observation_values(line))

    def _catch_notebook_observation_values(self, line):
        vals = {'observ_date': self.start_datetime.date(),
                'e_notebook_line_id': line.id,
                'student_id': self.student_id.id,
                'calendar_event_id': self.id}
        return vals

    def send_email_to_teachers_notebook_observation(self):
        template = self.env.ref(
            'education_notebook_observation.notebook_observation_teacher',
            False)
        if template:
            for observation in self.calendar_event_notebook_observation_ids:
                wizard = self.env['mail.compose.message'].with_context(
                    default_composition_mode='mass_mail',
                    default_template_id=template and template.id or False,
                    default_use_template=True,
                    active_id=observation.id,
                    active_ids=observation.ids,
                    active_model='education.notebook.observation',
                    default_model='education.notebook.observation',
                    default_res_id=observation.id,
                    force_send=True
                ).create({'subject': template.subject,
                          'body': template.body_html})
                wizard.send_mail()
