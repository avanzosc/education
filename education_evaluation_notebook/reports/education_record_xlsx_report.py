# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EducationGroupXlsx(models.AbstractModel):
    _name = "report.education.education_record_xlsx"
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

    def create_group_sheet(self, workbook, group):
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

        sheet = workbook.add_worksheet(group.description)

        sheet.merge_range("A1:E1", _("STUDENT LIST"), title_format)
        sheet.merge_range("A2:B2", _("Education Center:"), header_format)
        sheet.merge_range(
            "C2:E2", group.center_id.display_name, subheader_format)
        sheet.merge_range("A3:B3", _("Academic Year:"), header_format)
        sheet.merge_range(
            "C3:E3", group.academic_year_id.display_name, subheader_format)
        sheet.merge_range("A4:B4", _("Evaluation:"), header_format)
        sheet.merge_range("A5:B5", _("Education Course"), header_format)
        sheet.merge_range(
            "C5:E5", group.course_id.description, subheader_format)
        sheet.merge_range("A6:E6", group.description, header_format)

        sheet.write("A7", _("Index"), subheader_format)
        sheet.write("B7", _("Student"), subheader_format)
        sheet.write("C7", _("Birthdate"), subheader_format)
        sheet.write("D7", _("VAT Number"), subheader_format)

        sheet.set_column("A:A", 8)
        sheet.set_column("B:C", 40)
        sheet.set_column("D:D", 17)
        return sheet

    def add_subject_list(self, sheet, subject_lists):
        col = 5
        for subject in subject_lists:
            sheet.write(6, col, subject.description)
            col += 3

    def fill_student_row_data(
            self, sheet, row, student, eval_type, subject_lists):
        record_obj = self.env["education.record"]
        sheet.write("A" + str(row), str(row - 7))
        sheet.write("B" + str(row), student.display_name)
        sheet.write("C" + str(row), self._format_date(student.birthdate_date))
        sheet.write("D" + str(row), student.vat or "")
        column_num = 5
        row_num = row - 1
        for subject in subject_lists:
            records = record_obj.search([
                ("student_id", "=", student.id),
                ("subject_id", "=", subject.id),
                ("eval_type", "=", eval_type),
            ])
            eval_records = records.filtered(lambda r: r.evaluation_competence)
            if eval_records[:1].state != "not_evaluated":
                sheet.write(row_num, column_num, eval_records[:1].numeric_mark)
                sheet.write(row_num, column_num + 1,
                            eval_records[:1].n_mark_reduced_name)
                sheet.write(row_num, column_num + 2,
                            eval_records[:1].behaviour_mark_id.display_name)
            column_num += 3

    def generate_xlsx_report(self, workbook, data, objects):
        record_obj = self.env["education.record"]
        today = fields.Date.context_today(self)
        objects = objects.filtered(
            lambda g: g.group_type_id.type == "official")
        if not objects:
            raise UserError(
                _("You can only get xlsx report of official groups"))
        for group in objects:
            group_sheet = self.create_group_sheet(workbook, group)
            row = 8
            current_eval = group.academic_year_id.evaluation_ids.filtered(
                lambda e: e.date_start <= today <= e.date_end and
                e.center_id == group.center_id and
                e.course_id == group.course_id)
            group_records = record_obj.search([
                ("student_id", "in", group.student_ids.ids),
                ("eval_type", "=", current_eval[:1].eval_type),
            ])
            subject_lists = group_records.mapped("subject_id")
            self.add_subject_list(group_sheet, subject_lists)
            for student in group.student_ids:
                self.fill_student_row_data(
                    group_sheet, row, student, current_eval.eval_type,
                    subject_lists)
                row += 1
