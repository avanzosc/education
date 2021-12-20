# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class PartnerRecordReport(models.AbstractModel):
    _name = "report.education_evaluation_notebook.report_partner_record"
    _description = "Report Card"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get("form"):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        report = self.env["ir.actions.report"]._get_report_from_name(
            "education_evaluation_notebook.education_partner_record")
        partners = self.env["res.partner"].browse(data["ids"])
        academic_year_id = data["form"].get("academic_year_id", False)
        eval_type = data["form"].get("eval_type", "final")
        without_decimals = data["form"].get("without_decimals", False)
        return {
            "doc_ids": data["ids"],
            "doc_model": report.model,
            "docs": partners,
            "academic_year_id": academic_year_id and academic_year_id[0],
            "eval_type": eval_type,
            "without_decimals": without_decimals,
        }
