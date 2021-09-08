# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EducationBusGroupListReport(models.AbstractModel):
    _name = "report.fleet_route_education.report_education_bus_group"
    _description = "Bus List Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get("form"):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        passenger_report = self.env["ir.actions.report"]._get_report_from_name(
            "fleet_route_education.education_bus_group_list")
        groups = self.env["education.group"].browse(data["ids"])
        return {
            "doc_ids": data["ids"],
            "doc_model": passenger_report.model,
            "docs": groups,
            "selected_date": fields.Date.from_string(data["form"]["date"]),
        }
