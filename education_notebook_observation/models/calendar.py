# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields

from odoo.addons.education_evaluation_notebook.models.\
    education_academic_year_evaluation import EVAL_TYPE


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    calendar_event_notebook_observation_ids = fields.One2many(
        string='Notebook observations', inverse_name='calendar_event_id',
        comodel_name='education.notebook.observation')
    eval_type = fields.Selection(
        selection=EVAL_TYPE, string="Evaluation Season")

    def get_related_notebook_lines(self):
        self.ensure_one()
        notebook_lines = self.student_id.get_notebook_lines(
            academic_year=self.supervised_year_id.school_year_id,
            eval_type=self.eval_type)
        return notebook_lines.filtered("exists_master")

    def generate_notebook_observations(self, notebook_lines):
        self.ensure_one()
        observation_obj = self.env['education.notebook.observation']
        created_lines = self.mapped(
            "calendar_event_notebook_observation_ids.e_notebook_line_id")
        for line in notebook_lines.filtered(lambda l: l not in created_lines):
            observation_obj.create(
                self._catch_notebook_observation_values(line))

    def _catch_notebook_observation_values(self, line):
        self.ensure_one()
        vals = {
            "observ_date": self.start_datetime.date(),
            "e_notebook_line_id": line.id,
            "student_id": self.student_id.id,
            "calendar_event_id": self.id
        }
        return vals

    def send_email_to_teachers_notebook_observation(self):
        template = self.env.ref(
            "education_notebook_observation.notebook_observation_teacher",
            False)
        if template:
            for observation in self.calendar_event_notebook_observation_ids:
                template.with_context(
                    lang=observation.teacher_id.user_id.lang).send_mail(
                        observation.id, force_send=True)


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    center_id = fields.Many2one(
        string='Education Center', related='event_id.center_id', store=True)
