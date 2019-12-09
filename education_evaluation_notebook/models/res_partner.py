# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    academic_record_ids = fields.One2many(
        comodel_name="education.record", inverse_name="student_id",
        string="Academic Records")
    academic_record_count = fields.Integer(
        string="# Academic Record", compute="_compute_academic_record_count")

    @api.multi
    @api.depends("academic_record_ids")
    def _compute_academic_record_count(self):
        for partner in self.filtered("academic_record_ids"):
            partner.academic_record_count = len(partner.academic_record_ids)

    @api.multi
    def button_show_student_records(self):
        self.ensure_one()
        action = self.env.ref(
            "education_evaluation_notebook.education_record_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("student_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
