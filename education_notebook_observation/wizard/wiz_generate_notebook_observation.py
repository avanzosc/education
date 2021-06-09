# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class WizGenerateNotebookObservation(models.TransientModel):
    _name = "wiz.generate.notebook.observation"
    _description = "Wizard for generate notebook observations"

    line_ids = fields.One2many(
        string="Lines", comodel_name="wiz.generate.notebook.observation.line",
        inverse_name="wiz_id")

    @api.model
    def default_get(self, fields):
        result = super(
            WizGenerateNotebookObservation, self).default_get(fields)
        if self.env.context.get("active_id"):
            calendar = self.env["calendar.event"].browse(
                self.env.context.get("active_id"))
            notebook_lines = calendar.get_related_notebook_lines()
            observations = [
                (0, 0, {"education_notebook_line_id": x.id,
                        "teacher_id": x.teacher_id.id})
                for x in notebook_lines.filtered(
                    lambda l: l not in calendar.mapped(
                        "calendar_event_notebook_observation_ids."
                        "e_notebook_line_id"))]
            result.update({"line_ids": observations})
        return result

    @api.multi
    def button_generate_notebook_observations(self):
        context = dict(self._context or {})
        active_id = context.get("active_id", []) or []
        calendar = self.env["calendar.event"].browse(active_id)
        if calendar and self.line_ids:
            notebook_lines = self.sudo().line_ids.mapped(
                "education_notebook_line_id")
            calendar.generate_notebook_observations(notebook_lines)
        return {"type": "ir.actions.act_window_close"}


class WizGenerateNotebookObservationLine(models.TransientModel):
    _name = "wiz.generate.notebook.observation.line"
    _description = "lines of wizard for generate notebook observations"

    wiz_id = fields.Many2one(
        string="Wizard", comodel_name="wiz.generate.notebook.observation")
    education_notebook_line_id = fields.Many2one(
        string="Education Notebook Line",
        comodel_name="education.notebook.line")
    teacher_id = fields.Many2one(
        string="Teacher", comodel_name="hr.employee")
