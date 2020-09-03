# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EducationGroupXlsx(models.AbstractModel):
    _name = "report.education.education_group_xlsx"
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
        title_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vjustify",
        })
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

        sheet = workbook.add_worksheet(book.description)

        sheet.merge_range("A1:E1", _("STUDENT LIST"), title_format)
        sheet.merge_range("A2:B2", _("Education Center:"), header_format)
        sheet.merge_range(
            "C2:E2", book.center_id.display_name, subheader_format)
        sheet.merge_range("A3:B3", _("Academic Year:"), header_format)
        sheet.merge_range(
            "C3:E3", book.academic_year_id.display_name, subheader_format)
        sheet.merge_range("A4:B4", _("Education Course"), header_format)
        sheet.merge_range(
            "C4:E4", book.course_id.description, subheader_format)
        sheet.merge_range("A5:E5", book.description, header_format)

        sheet.write("A7", _("Index"), subheader_format)
        sheet.write("B7", _("Surnames"), subheader_format)
        sheet.write("C7", _("Name"), subheader_format)
        sheet.write("D7", _("Birthdate"), subheader_format)
        sheet.write("E7", _("VAT Number"), subheader_format)

        sheet.set_column("A:A", 8)
        sheet.set_column("B:C", 40)
        sheet.set_column("D:D", 17, date_format)
        sheet.set_column("E:E", 17)
        return sheet

    def fill_student_row_data(self, sheet, row, student, academic_year):
        sheet.write("A" + str(row), str(row - 7))
        sheet.write("B" + str(row),
                    "{} {}".format(student.lastname or "",
                                   student.lastname2 or ""))
        sheet.write("C" + str(row), student.firstname or "")
        sheet.write("D" + str(row), self._format_date(student.birthdate_date))
        sheet.write("E" + str(row), student.vat or "")

    def generate_xlsx_report(self, workbook, data, objects):
        objects = objects.filtered(
            lambda g: g.group_type_id.type == "official")
        if not objects:
            raise UserError(
                _("You can only get xlsx report of official groups"))
        for group in objects:
            group_sheet = self.create_group_sheet(workbook, group)
            row = 8
            for student in group.student_ids:
                self.fill_student_row_data(
                    group_sheet, row, student, group.academic_year_id)
                row += 1
