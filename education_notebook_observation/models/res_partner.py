# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = 'res.partner'

    student_notebook_observation_ids = fields.One2many(
        string='Notebook observations', inverse_name='student_id',
        comodel_name='education.notebook.observation')
    observation_count = fields.Integer(
        string="# Observations", compute="_compute_observation_count")

    @api.multi
    @api.depends("student_notebook_observation_ids")
    def _compute_observation_count(self):
        for partner in self.filtered("student_notebook_observation_ids"):
            partner.observation_count = len(
                partner.student_notebook_observation_ids)

    @api.multi
    def button_show_student_observations(self):
        self.ensure_one()
        action = self.env.ref(
            "education_notebook_observation."
            "education_notebook_observation_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("student_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
