# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EducationGroupXlsx(models.AbstractModel):
    _name = "report.contacts_school_education.partner_insurance_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def _format_date(self, date):
        # format date following user language
        if not date:
            return False
        lang_model = self.env["res.lang"]
        lang = lang_model._lang_get(self.env.user.lang)
        date_format = lang.date_format
        return datetime.strftime(
            fields.Date.from_string(date), date_format)

    def create_group_sheet(self, workbook, book):
        header_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vjustify",
            "fg_color": "#F2F2F2",
        })
        subheader_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vjustify",
        })
        date_format = workbook.add_format({"num_format": "dd/mm/yyyy"})

        sheet = workbook.add_worksheet(book.display_name)

        sheet.merge_range("A1:G1", _("Student"), header_format)
        sheet.merge_range("H1:K1", _("Progenitor 1"), header_format)
        sheet.merge_range("L1:O1", _("Progenitor 2"), header_format)

        sheet.write("A2", _("Index"), subheader_format)
        sheet.write("B2", _("Surname 1"), subheader_format)
        sheet.write("C2", _("Surname 2"), subheader_format)
        sheet.write("D2", _("Name"), subheader_format)
        sheet.write("E2", _("Birthdate"), subheader_format)
        sheet.write("F2", _("Education Course"), subheader_format)
        sheet.write("G2", _("Insured"), subheader_format)
        sheet.write("H2", _("Surname 1"), subheader_format)
        sheet.write("I2", _("Surname 2"), subheader_format)
        sheet.write("J2", _("Name"), subheader_format)
        sheet.write("K2", _("VAT Number"), subheader_format)
        sheet.write("L2", _("Surname 1"), subheader_format)
        sheet.write("M2", _("Surname 2"), subheader_format)
        sheet.write("N2", _("Name"), subheader_format)
        sheet.write("O2", _("VAT Number"), subheader_format)

        sheet.set_column("A:A", 8)
        sheet.set_column("B:D", 20)
        sheet.set_column("E:E", 17, date_format)
        sheet.set_column("F:F", 30)
        sheet.set_column("H:J", 20)
        sheet.set_column("K:K", 15)
        sheet.set_column("L:N", 20)
        sheet.set_column("O:O", 15)
        return sheet

    def fill_student_row_data(self, sheet, row, student):
        sheet.write("A" + str(row), str(row - 2))
        sheet.write("B" + str(row), student.lastname or "")
        sheet.write("C" + str(row),  student.lastname2 or "")
        sheet.write("D" + str(row), student.firstname or "")
        sheet.write("E" + str(row), self._format_date(student.birthdate_date))
        sheet.write(
            "F" + str(row), student.current_course_id.description or "")
        sheet.write("G" + str(row), student.insured_partner_count or 0)
        if student.insured_partner_count >= 1:
            progenitor1 = student.insured_partner_ids[0]
            sheet.write("H" + str(row), progenitor1.lastname or "")
            sheet.write("I" + str(row), progenitor1.lastname2 or "")
            sheet.write("J" + str(row), progenitor1.firstname or "")
            sheet.write("K" + str(row), progenitor1.vat or "")
            if student.insured_partner_count > 1:
                progenitor2 = student.insured_partner_ids[1]
                sheet.write("L" + str(row), progenitor2.lastname or "")
                sheet.write("M" + str(row), progenitor2.lastname2 or "")
                sheet.write("N" + str(row), progenitor2.firstname or "")
                sheet.write("O" + str(row), progenitor2.vat or "")

    def generate_xlsx_report(self, workbook, data, objects):
        objects = objects.filtered(
            lambda c: c.educational_category == "school")
        if not objects:
            raise UserError(
                _("You can only get xlsx report of education centers"))
        for center in objects:
            group_sheet = self.create_group_sheet(workbook, center)
            row = 3
            for student in objects.search([
                    ("current_center_id", "=", center.id),
                    ("educational_category", "=", "student"),
                    ("has_insurance", "=", True),
                    ]):
                self.fill_student_row_data(group_sheet, row, student)
                row += 1
