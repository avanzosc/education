# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class EducationGroupXlsx(models.AbstractModel):
    _inherit = "report.education.education_group_xlsx"

    def create_group_sheet(self, workbook, book):
        sheet = super(EducationGroupXlsx, self).create_group_sheet(
            workbook, book)
        subheader_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vjustify",
        })

        sheet.write("G7", _("Extracurricular"), subheader_format)
        sheet.set_column("G:G", 40)
        return sheet

    def fill_student_row_data(self, sheet, row, student, academic_year):
        super(EducationGroupXlsx, self).fill_student_row_data(
            sheet, row, student, academic_year)
        group_type = self.env["education.group_type"].search([
            ("description", "=", "EXTRAESCOLARES"),
        ])
        extracurricular_groups = student.student_group_ids.filtered(
            lambda g: g.group_type_id == group_type and
            g.academic_year_id == academic_year
        )
        sheet.write(
            "G" + str(row),
            ", ".join(extracurricular_groups.mapped("description"))
            if extracurricular_groups else "")
