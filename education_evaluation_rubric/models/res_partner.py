# Copyright 2023 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def get_academic_records_non_curricular_rubrics(
            self, academic_year, eval_type=False):
        self.ensure_one()
        academic_records = self.get_academic_records_non_curricular(
            academic_year=academic_year, eval_type=eval_type
        )
        return academic_records.mapped("child_record_ids").filtered(
            lambda r: r.n_line_id.competence_id.eval_mode == "rubric")
