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

    def __init__(self, pool, cr):
        # main sheet which will contains report
        self.sheet = None

        # columns of the report
        self.columns = None

        # row_pos must be incremented at each writing lines
        self.row_pos = None

        # Formats
        self.format_right = None
        self.format_left = None
        self.format_right_bold_italic = None
        self.format_bold = None
        self.format_header_left = None
        self.format_header_center = None
        self.format_header_right = None
        self.format_header_amount = None
        self.format_amount = None
        self.format_percent_bold_italic = None

    def _format_date(self, date):
        # format date following user language
        if not date:
            return False
        lang_model = self.env["res.lang"]
        lang = lang_model._lang_get(self.env.user.lang)
        date_format = lang.date_format
        return datetime.strftime(
            fields.Date.from_string(date), date_format)

    def create_group_sheet(self, workbook, group, current_eval):
        sheet = workbook.add_worksheet(group.description)

        sheet.merge_range(
            "A1:D1", _("STUDENT LIST"), self.format_header_center)
        sheet.merge_range(
            "A2:B2", _("Education Center:"), self.format_header_right)
        sheet.merge_range(
            "C2:D2", group.center_id.display_name, self.format_left)
        sheet.merge_range(
            "A3:B3", _("Academic Year:"), self.format_header_right)
        sheet.merge_range(
            "C3:D3", group.academic_year_id.display_name, self.format_left)
        sheet.merge_range("A4:B4", _("Evaluation:"), self.format_header_right)
        field = current_eval._fields["eval_type"]
        eval_type = field.convert_to_export(
            current_eval["eval_type"], current_eval)
        sheet.merge_range("C4:D4", eval_type, self.format_left)
        sheet.merge_range(
            "A5:B5", _("Education Course"), self.format_header_right)
        sheet.merge_range(
            "C5:D5", group.course_id.description, self.format_left)
        sheet.merge_range(
            "A6:B6", _("Education Group"), self.format_header_right)
        sheet.merge_range("C6:D6", group.description, self.format_left)

        sheet.write("A7", "#", self.format_header_center)
        sheet.merge_range("B7:D7", _("Student"), self.format_header_center)

        sheet.set_column("A:A", 3)
        sheet.set_column("B:D", 15)
        return sheet

    def add_subject_list(self, sheet, subject_lists):
        col = 4
        for subject in subject_lists:
            sheet.merge_range(
                6, col, 6, col + 2, subject.description,
                self.format_header_center)
            col += 3

    def fill_student_row_data(
            self, sheet, row, student, eval_type, subject_lists):
        not_passed = [
            self.env.ref(
                "education_evaluation_notebook.numeric_mark_insufficient"),
            self.env.ref(
                "education_evaluation_notebook.numeric_mark_very_bad")]
        record_obj = self.env["education.record"]
        sheet.write("A" + str(row), str(row - 7), self.format_border)
        sheet.write("B" + str(row), student.lastname, self.format_border)
        sheet.write("C" + str(row), student.lastname2, self.format_border)
        sheet.write("D" + str(row), student.firstname, self.format_border)
        column_num = 4
        row_num = row - 1
        for subject in subject_lists:
            records = record_obj.search([
                ("student_id", "=", student.id),
                ("subject_id", "=", subject.id),
                ("eval_type", "=", eval_type),
                ("evaluation_competence", "=", True),
            ])
            sheet.set_column(column_num, column_num + 2, 5)
            if not records:
                sheet.write(row_num, column_num, "XX", self.format_border)
                sheet.write(row_num, column_num + 1, "XX", self.format_border)
                sheet.write(row_num, column_num + 2, "XX", self.format_border)
            else:
                record = records[:1]
                num_mark = record.numeric_mark
                num_mark_name = record.n_mark_reduced_name
                behaviour = record.behaviour_mark_id.display_name or _("UN")
                if record.exceptionality in ["exempt", "not_taken"]:
                    text = (
                        _("Exempt") if record.exceptionality == "exempt" else
                        _("Not Taken"))
                    sheet.merge_range(
                        row_num, column_num, row_num, column_num + 2,
                        text, self.format_center_bold)
                else:
                    format_amount = self.format_amount
                    format_mark = self.format_border
                    format_behaviour = self.format_border
                    if record.state == "assessed":
                        format_amount = self.format_amount_bold
                        format_mark = self.format_bold
                        if record.mark_id in not_passed:
                            format_amount = self.format_amount_bold_not_passed
                            format_mark = self.format_bold_not_passed
                        if (record.behaviour_mark_id.code not in
                                ('A', 'B', 'C')):
                            format_behaviour = self.format_bold_not_passed
                    elif record.mark_id in not_passed:
                        format_amount = self.format_amount_not_passed
                        format_mark = self.format_border_not_passed
                    if record.behaviour_mark_id.code not in ('A', 'B', 'C'):
                        format_behaviour = self.format_border_not_passed
                    sheet.write_number(
                        row_num, column_num, float(num_mark), format_amount)
                    sheet.write(
                        row_num, column_num + 1, num_mark_name, format_mark)
                    sheet.write(
                        row_num, column_num + 2, behaviour, format_behaviour)

            column_num += 3

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        record_obj = self.env["education.record"]
        today = fields.Date.context_today(self)
        objects = objects.filtered(
            lambda g: g.group_type_id.type == "official")
        if not objects:
            raise UserError(
                _("You can only get xlsx report of official groups"))
        for group in objects:
            current_eval = group.academic_year_id.evaluation_ids.filtered(
                lambda e: e.date_start <= today <= e.date_end and
                e.center_id == group.center_id and
                e.course_id == group.course_id)
            group_sheet = self.create_group_sheet(
                workbook, group, current_eval)
            row = 8
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

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Those formats can be used on all cell.
        """
        self.format_border = workbook.add_format({'border': True})
        self.format_border_not_passed = workbook.add_format(
            {'border': True, 'color': '#FF0000'})
        self.format_bold = workbook.add_format({'bold': True, 'border': True})
        self.format_bold_not_passed = workbook.add_format(
            {'bold': True, 'border': True, 'color': '#FF0000'})
        self.format_right = workbook.add_format({'align': 'right'})
        self.format_left = workbook.add_format({'align': 'left'})
        self.format_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True, 'border': True})
        self.format_right_bold_italic = workbook.add_format(
            {'align': 'right', 'bold': True, 'italic': True})
        self.format_header_left = workbook.add_format(
            {'bold': True, 'border': True, 'bg_color': '#F2F2F2'})
        self.format_header_center = workbook.add_format(
            {'bold': True, 'align': 'center', 'border': True,
             'bg_color': '#F2F2F2'})
        self.format_header_right = workbook.add_format(
            {'bold': True, 'align': 'right', 'border': True,
             'bg_color': '#F2F2F2'})
        self.format_header_amount = workbook.add_format(
            {'bold': True, 'border': True, 'bg_color': '#F2F2F2'})
        self.format_amount = workbook.add_format({'border': True})
        self.format_amount.set_num_format('#,##0.' + '00')
        self.format_amount_not_passed = workbook.add_format({
            'color': '#FF0000', 'border': True})
        self.format_amount_not_passed.set_num_format('#,##0.' + '00')
        self.format_amount_not_evaluated = workbook.add_format({
            'color': '#B5B5B5', 'border': True})
        self.format_amount_not_evaluated.set_num_format('#,##0.' + '00')
        self.format_amount_bold = workbook.add_format({'bold': True})
        self.format_amount_bold.set_num_format('#,##0.' + '00')
        self.format_amount_bold_not_passed = workbook.add_format({
            'bold': True, 'color': '#FF0000'})
        self.format_amount_bold_not_passed.set_num_format('#,##0.' + '00')
