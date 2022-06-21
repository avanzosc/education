# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from statistics import mean

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EducationGroupXlsx(models.AbstractModel):
    _name = "report.education.education_record_all_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def __init__(self, pool, cr):
        # main sheet which will contains report
        self.sheet = None

        # columns of the report
        self.columns = None

        # row_pos must be incremented at each writing lines
        self.row_pos = None

        # Formats
        self.format_border = None
        self.format_border_final = None
        self.format_bold = None
        self.format_bold_not_passed = None
        self.format_right = None
        self.format_left = None
        self.format_center_bold = None
        self.format_right_bold_italic = None
        self.format_header_left = None
        self.format_header_center = None
        self.format_header_right = None
        self.format_header_amount = None
        self.format_amount = None
        self.format_amount_not_passed = None
        self.format_amount_not_passed_final = None
        self.format_amount_bold = None
        self.format_amount_bold_final = None
        self.format_amount_bold_not_passed = None
        self.format_integer_statistics = None

    def _get_not_passed(self):
        return [
            self.env.ref(
                "education_evaluation_notebook.numeric_mark_insufficient"),
            self.env.ref(
                "education_evaluation_notebook.numeric_mark_very_bad")]

    def create_group_sheet(self, workbook, group):
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
        sheet.merge_range(
            "A4:B4", _("Education Course"), self.format_header_right)
        sheet.merge_range(
            "C4:D4", group.course_id.description, self.format_left)
        sheet.merge_range(
            "A5:B5", _("Education Group"), self.format_header_right)
        sheet.merge_range("C5:D5", group.description, self.format_left)

        sheet.write("A7", "#", self.format_header_center)
        sheet.merge_range("B7:D7", _("Student"), self.format_header_center)

        sheet.set_column("A:A", 3)
        sheet.set_column("B:D", 15)
        return sheet

    def add_subject_list(self, sheet, subject_lists):
        sheet.write(6, 4, _("Evaluation"), self.format_header_center)
        sheet.write(6, 5, _("Not Passed"), self.format_header_center)
        col = 6
        for subject in subject_lists:
            sheet.merge_range(
                6, col, 6, col + 1, subject.description,
                self.format_header_center)
            col += 2
        sheet.write(6, col, _("Average Score"), self.format_header_center)

    def add_record(self, sheet, row_num, column_num, eval_type, record):
        not_passed = self._get_not_passed()
        format_border = (
            self.format_border if eval_type != "final" else
            self.format_border_final)
        mark_name = record.mark_id
        if record.exceptionality:
            field = record._fields["exceptionality"]
            text = field.convert_to_export(
                record.exceptionality, record)
            if record.exceptionality in (
                "adaptation", "reinforcement", "pending", "neae"):
                text = "{} ({})".format(float(record.numeric_mark), text)
            sheet.write(
                row_num, column_num, text, format_border)
        else:
            format_amount = (
                self.format_amount if eval_type != "final" else
                self.format_amount_final)
            if record.state == "assessed":
                format_amount = (
                    self.format_amount_bold
                    if eval_type != "final" else
                    self.format_amount_bold_final)
            elif mark_name in not_passed:
                # not_passed_count += 1
                format_amount = (
                    self.format_amount_not_passed
                    if eval_type != "final" else
                    self.format_amount_not_passed_final)
            sheet.write_number(
                row_num, column_num, float(record.numeric_mark),
                format_amount)

    def select_higher_mark(self, ordinary, extraordinary):
        if not extraordinary:
            return ordinary
        else:
            if extraordinary.numeric_mark >= ordinary.numeric_mark:
                return extraordinary
            else:
                return ordinary

    def fill_student_row_data(
            self, sheet, student_num, student, subject_lists, academic_year):
        not_passed = self._get_not_passed()
        record_obj = self.env["education.record"]
        row = 8 + (4 * (student_num - 1))
        sheet.write("A" + str(row), str(student_num), self.format_border)
        sheet.write("B" + str(row), student.lastname or "", self.format_left)
        sheet.write("C" + str(row), student.lastname2 or "", self.format_left)
        sheet.write("D" + str(row), student.firstname or "", self.format_left)
        column_num = 6
        row_num = row - 1
        for eval_type in ["first", "second", "third", "final"]:
            mark_list = []
            not_passed_count = 0
            evaluation_obj = self.env["education.academic_year.evaluation"]
            field = evaluation_obj._fields["eval_type"]
            eval_type_text = field.convert_to_export(
                eval_type, evaluation_obj)
            sheet.write(row_num, 4, eval_type_text)
            format_border = (
                self.format_border if eval_type != "final" else
                self.format_border_final)
            for subject in subject_lists:
                domain = [
                    ("n_line_id.schedule_id.academic_year_id", "=",
                     academic_year.id),
                    ("student_id", "=", student.id),
                    ("subject_id", "=", subject.id),
                    ("eval_type", "=", eval_type),
                    "|", ("evaluation_competence", "=", True),
                    ("global_competence", "=", True),
                ]
                records = record_obj.sudo().search(domain)
                sheet.set_column(column_num, column_num + 2, 7)
                ordinary = records.filtered(
                    lambda r: not r.recovered_record_id)[:1]
                if not ordinary:
                    data = "XX"
                    sheet.write(row_num, column_num, data, format_border)
                else:
                    self.add_record(
                        sheet, row_num, column_num, eval_type, ordinary)
                column_num += 1
                extraordinary = records.filtered("recovered_record_id")[:1]
                if not extraordinary:
                    data = "-"
                    sheet.write(row_num, column_num, data, format_border)
                else:
                    self.add_record(
                        sheet, row_num, column_num, eval_type, extraordinary)
                column_num += 1
                mark = self.select_higher_mark(ordinary, extraordinary)
                if mark:
                    mark_list.append(mark.numeric_mark)
                    if mark.mark_id in not_passed:
                        not_passed_count += 1
            sheet.write(
                row_num, 5, not_passed_count, self.format_integer_statistics)
            avg_mark = mean(mark_list) if mark_list else 0
            avg_mark_name = self.env[
                "education.mark.numeric"]._get_mark(avg_mark)
            sheet.write(
                row_num, column_num, avg_mark,
                self.format_amount_not_passed_statistics
                if avg_mark_name in not_passed else
                self.format_amount_statistics)
            row_num += 1
            column_num = 6

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        record_obj = self.env["education.record"]
        if not objects:
            raise UserError(
                _("You can only get xlsx report of education groups"))
        for group in objects:
            group_sheet = self.create_group_sheet(workbook, group)
            group_records = record_obj.sudo().search([
                ("student_id", "in", group.student_ids.ids),
                ("n_line_id.schedule_id.task_type_id.education_code", "!=",
                 "0123"),
                ("n_line_id.schedule_id.academic_year_id", "=",
                 group.academic_year_id.id),
            ])
            subject_lists = group_records.mapped("subject_id")
            self.add_subject_list(group_sheet, subject_lists)
            student_num = 1
            for student in group.student_ids:
                self.fill_student_row_data(
                    group_sheet, student_num, student, subject_lists,
                    group.academic_year_id)
                student_num += 1

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Those formats can be used on all cell.
        """
        self.format_border = workbook.add_format({
            'border': True,
            'align': 'center',
        })
        self.format_border_final = workbook.add_format({
            'border': True,
            'align': 'center',
            'bg_color': '#DBDBDB',
        })
        self.format_bold = workbook.add_format({
            'bold': True,
            'border': True,
            'align': 'center',
        })
        self.format_bold_not_passed = workbook.add_format({
            'bold': True,
            'border': True,
            'align': 'center',
            'color': '#FF0000',
        })
        self.format_right = workbook.add_format({
            'border': True,
            'align': 'right',
        })
        self.format_left = workbook.add_format({
            'border': True,
            'align': 'left',
        })
        self.format_right_bold_italic = workbook.add_format({
            'align': 'right',
            'bold': True,
            'italic': True,
        })

        header_dict = {
            'bold': True,
            'border': True,
            'bg_color': '#F2F2F2'
        }
        self.format_header_left = workbook.add_format(header_dict)
        self.format_header_center = workbook.add_format(header_dict)
        self.format_header_center.set_align('center')
        self.format_header_right = workbook.add_format(header_dict)
        self.format_header_right.set_align('right')
        self.format_header_amount = workbook.add_format(header_dict)
        self.format_header_amount.set_num_format('#,##0.' + '00')
        self.format_amount = workbook.add_format({'border': True})
        self.format_amount.set_num_format('#,##0.' + '00')
        self.format_amount_final = workbook.add_format({
            'border': True,
            'bg_color': '#DBDBDB',
        })
        self.format_amount_final.set_num_format('#,##0.' + '00')
        self.format_amount_not_passed = workbook.add_format({
            'color': '#FF0000', 'border': True})
        self.format_amount_not_passed.set_num_format('#,##0.' + '00')
        self.format_amount_not_passed_final = workbook.add_format({
            'color': '#FF0000',
            'border': True,
            'bg_color': '#DBDBDB',
        })
        self.format_amount_not_passed_final.set_num_format('#,##0.' + '00')
        self.format_amount_bold = workbook.add_format({
            'bold': True,
            'border': True,
        })
        self.format_amount_bold.set_num_format('#,##0.' + '00')
        self.format_amount_bold_final = workbook.add_format({
            'bold': True,
            'border': True,
            'bg_color': '#DBDBDB',
        })
        self.format_amount_bold_final.set_num_format('#,##0.' + '00')
        self.format_amount_bold_not_passed = workbook.add_format({
            'bold': True,
            'border': True,
            'color': '#FF0000',
        })
        self.format_amount_bold_not_passed.set_num_format('#,##0.' + '00')

        statistics_dict = {
            'bold': True,
            'border': True,
            'align': 'center',
            'bg_color': '#92BDDA'
        }
        self.format_statistics = workbook.add_format(statistics_dict)
        self.format_percentage = workbook.add_format(statistics_dict)
        self.format_percentage.set_num_format(10)
        self.format_integer_statistics = workbook.add_format(statistics_dict)
        self.format_integer_statistics.set_num_format(1)
        self.format_amount_statistics = workbook.add_format(statistics_dict)
        self.format_amount_statistics.set_num_format(
            '#,##0.' + '00')
        self.format_amount_not_passed_statistics = workbook.add_format(
            statistics_dict)
        self.format_amount_not_passed_statistics.set_num_format(
            '#,##0.' + '00')
