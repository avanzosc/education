# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class WizSendNotebookObservationEmail(models.TransientModel):
    _name = "wiz.send.notebook.observation.email"
    _description = "Wizard for send email to teachers"

    @api.multi
    def button_send_email(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', []) or []
        calendar = self.env['calendar.event'].browse(active_id)
        if calendar and calendar.calendar_event_notebook_observation_ids:
            calendar.send_email_to_teachers_notebook_observation()
        return {'type': 'ir.actions.act_window_close'}
