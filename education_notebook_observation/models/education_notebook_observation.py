# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class EducationNotebookObservation(models.Model):
    _name = "education.notebook.observation"
    _description = "Education notebook observation"
    _order = "observ_date, e_notebook_line_id, teacher_id, student_id"

    @api.depends("observations")
    def _compute_state(self):
        for observation in self:
            observation.state = (
                "included" if observation.observations else "pending")

    observ_date = fields.Date(
        string="Date")
    e_notebook_line_id = fields.Many2one(
        string="Education notebook line",
        comodel_name="education.notebook.line")
    teacher_id = fields.Many2one(
        string="Teacher", comodel_name="hr.employee",
        related="e_notebook_line_id.teacher_id", store=True)
    student_id = fields.Many2one(
        string="Student", comodel_name="res.partner",
        domain=[("educational_category", "=", "student")])
    calendar_event_id = fields.Many2one(
        string="Meeting", comodel_name="calendar.event")
    education_center_id = fields.Many2one(
        string="Education Center", comodel_name="res.partner",
        related="calendar_event_id.center_id", store=True)
    observations = fields.Text(
        string="Observations")
    state = fields.Selection(
        selection=[("pending", "Pending"),
                   ("included", "Included"), ],
        default="pending", track_visibility="onchange",
        compute="_compute_state", store=True)
    event_teacher_id = fields.Many2one(
        comodel_name="hr.employee", string="Meeting Teacher",
        related="calendar_event_id.teacher_id")

    @api.multi
    def get_eval_type(self):
        self.ensure_one()
        line = self.e_notebook_line_id
        field = line._fields["eval_type"]
        eval_type = field.convert_to_export(line["eval_type"], line)
        return eval_type
