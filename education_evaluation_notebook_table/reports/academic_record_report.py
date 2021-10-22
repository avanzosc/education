
import logging
import string
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AcademicRecordReport(models.AbstractModel):
    _name = "report.education_evaluation_notebook_table.academic_record"
    _inherit = "report.report_xlsx.abstract"

    def create_schedule_sheet(self, workbook, book):
        base_format_vals = {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vjustify",
        }
        title_format = workbook.add_format(base_format_vals)
        header_format_vals = dict(base_format_vals, fg_color="#F2F2F2")
        header_format = workbook.add_format(header_format_vals)
        subheader_format = workbook.add_format(base_format_vals)
        global_format_vals = dict(base_format_vals, fg_color="#4dff88")
        global_subheader_format = workbook.add_format(global_format_vals)
        eval_format_vals = dict(base_format_vals, fg_color="#ffff80")
        eval_subheader_format = workbook.add_format(eval_format_vals)
        competence_format_vals = dict(base_format_vals, fg_color="#e6e6e6")
        competence_subheader_format = workbook.add_format(competence_format_vals)

        sheet = workbook.add_worksheet(book.display_name)

        record_lines = book.record_ids.mapped('n_line_id')
        max_range = string.ascii_uppercase[len(record_lines) + book.exam_count]

        sheet.merge_range("A1:%s1" % max_range, _("SCHEDULE ACADEMIC RECORDS"), title_format)
        sheet.merge_range("A2:B2", _("Education Center:"), header_format)
        sheet.merge_range(
            "C2:%s2" % max_range, book.center_id.display_name, subheader_format)
        sheet.merge_range("A3:B3", _("Academic Year:"), header_format)
        sheet.merge_range(
            "C3:%s3" % max_range, book.academic_year_id.display_name, subheader_format)
        sheet.merge_range("A4:B4", _("Classroom"), header_format)
        sheet.merge_range(
            "C4:%s4" % max_range, book.classroom_id.description, subheader_format)
        sheet.merge_range("A5:%s5" % max_range, book.display_name, header_format)

        sheet.write("A7", _("Student"), subheader_format)

        for line in record_lines.filtered(lambda r: r.competence_id.global_check):
            pos = 1
            for eval_line in record_lines.filtered(lambda r: r.parent_line_id.id == line.id):
                for competence_line in record_lines.filtered(lambda r: r.parent_line_id.id == eval_line.id):
                    for exam_line in competence_line.exam_ids:
                        sheet.write("%s7" % string.ascii_uppercase[pos],
                                    exam_line.display_name,
                                    subheader_format)
                        pos += 1
                    sheet.write("%s7" % string.ascii_uppercase[pos],
                                competence_line.display_name,
                                competence_subheader_format)
                    pos += 1
                sheet.write("%s7" % string.ascii_uppercase[pos],
                            eval_line.display_name,
                            eval_subheader_format)
                pos += 1

            sheet.write("%s7" % string.ascii_uppercase[pos], line.display_name,
                        global_subheader_format)
            pos += 1

        sheet.set_column("A:A", 8)
        sheet.set_column("B:C", 40)
        sheet.set_column("D:D", 17)
        sheet.set_column("E:E", 17)
        return sheet

    def fill_student_row_data(self, sheet, row, student, schedule):
        sheet.write("A" + str(row),
                    "{} {}".format(student.lastname or "",
                                   student.lastname2 or ""))

        record_lines = schedule.record_ids.mapped('n_line_id')
        records = schedule.record_ids

        for line in record_lines.filtered(
                lambda r: r.competence_id.global_check):
            pos = 1
            for eval_line in record_lines.filtered(
                    lambda r: r.parent_line_id.id == line.id):
                for competence_line in record_lines.filtered(
                        lambda r: r.parent_line_id.id == eval_line.id):
                    for exam_line in competence_line.exam_ids:
                        exam = self._get_kid_record(student.id, records, exam_line.id)
                        exam_mark = exam.filtered(lambda c: c.exam_id)
                        sheet.write("%s%s" % (string.ascii_uppercase[pos], row), exam_mark.numeric_mark)
                        pos += 1
                    competence = self._get_kid_record(student.id, records, competence_line.id)
                    competence_mark = competence.filtered(lambda c: not c.exam_id)
                    sheet.write("%s%s" % (string.ascii_uppercase[pos], row), competence_mark.numeric_mark)
                    pos += 1
                eval = self._get_kid_record(student.id, records, eval_line.id)
                sheet.write("%s%s" % (string.ascii_uppercase[pos], row), eval.numeric_mark)
                pos += 1

            global_mark = self._get_kid_record(student.id, records, line.id)
            sheet.write("%s%s" % (string.ascii_uppercase[pos], row), global_mark.numeric_mark)
            pos += 1

    def generate_xlsx_report(self, workbook, data, objects):
        for schedule in objects:
            group_sheet = self.create_schedule_sheet(workbook, schedule)
            row = 8
            for student in schedule.student_ids:
                self.fill_student_row_data(
                    group_sheet, row, student, schedule)
                row += 1

    def _get_kid_record(self, kid_id, schedule_records, n_line_id):
        return schedule_records.filtered(
            lambda r: r.student_id.id == kid_id and r.n_line_id.id == n_line_id)

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            "doc_ids": docids,
            "doc_model": "education.schedule",
            "docs": self.env['education.schedule'].browse(docids),
            #'report_type': data.get('report_type') if data else '',
        }
