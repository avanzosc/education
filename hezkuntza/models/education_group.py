# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class EducationGroup(models.Model):
    _inherit = "education.group"

    education_code = fields.Char(default="/", readonly=True)

    @api.model
    def create(self, values):
        group_codes = self.search([
            ("center_id", "=", values.get("center_id")),
            ("academic_year_id", "=", values.get("academic_year_id")),
        ], order="education_code DESC").mapped("education_code")
        codes = [int(code) if code.isdigit() else 0 for code in group_codes]
        if values.get("education_code", "/") == "/":
            code_num = max(codes) + 1 if codes else 1
            values["education_code"] = str(code_num).rjust(8, "0")
        return super(EducationGroup, self).create(values)
