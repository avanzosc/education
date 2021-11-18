
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AcademicRecordReport(models.AbstractModel):
    _name = "report.education_schedule.academic_record"
    _inherit = "report.report_xlsx.abstract"

    def __init__(self, pool, cr):
        self.workbook = None
        self.title_format = None
        self.header_format = None
        self.subheader_format = None
        self.global_subheader_format = None
        self.eval_subheader_format = None
        self.competence_subheader_format = None
        self.base_mark_format_vals = None

    def create_schedule_sheet(self, workbook, book):

        sheet = workbook.add_worksheet(book.display_name)

        record_lines = book.record_ids.mapped('n_line_id')
        max_range = len(record_lines) + book.exam_count

        sheet.merge_range(
            0, 0, 0, max_range, _("SCHEDULE ACADEMIC RECORDS"),
            self.title_format)
        sheet.merge_range("A2:B2", _("Education Center:"), self.header_format)
        sheet.merge_range(
            1, 2, 1, max_range, book.center_id.display_name,
            self.subheader_format)
        sheet.merge_range("A3:B3", _("Academic Year:"), self.header_format)
        sheet.merge_range(
            2, 2, 2, max_range, book.academic_year_id.display_name,
            self.subheader_format)
        sheet.merge_range("A4:B4", _("Classroom"), self.header_format)
        sheet.merge_range(
            3, 2, 3, max_range, book.classroom_id.description,
            self.subheader_format)
        sheet.merge_range(
            4, 0, 4, max_range, book.display_name, self.header_format)

        sheet.write("A7", _("Student"), self.subheader_format)

        for line in record_lines.filtered(
                lambda r: r.competence_id.global_check):
            pos = 1
            for eval_line in record_lines.filtered(
                    lambda r: r.parent_line_id.id == line.id):
                for competence_line in record_lines.filtered(
                        lambda r: r.parent_line_id.id == eval_line.id):
                    for exam_line in competence_line.exam_ids:
                        sheet.write(6, pos,
                                    exam_line.display_name,
                                    self.subheader_format)
                        sheet.set_column(6, pos, 10)
                        pos += 1
                    sheet.write(6, pos,
                                competence_line.display_name,
                                self.competence_subheader_format)
                    sheet.set_column(6, pos, 20)
                    pos += 1
                sheet.write(6, pos,
                            eval_line.display_name,
                            self.eval_subheader_format)
                sheet.set_column(6, pos, 20)
                pos += 1

            sheet.write(6, pos, line.display_name,
                        self.global_subheader_format)
            pos += 1

        sheet.set_column("A:A", 35)
        return sheet

    def fill_student_row_data(self, sheet, row,
                              student, schedule, eval_type=None):
        sheet.write(row, 0, student.name)

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
                        exam = self._get_kid_exam_record(
                            student.id, records, exam_line.id)
                        mark_format = self.get_record_format(
                            exam.numeric_mark, exam.state)
                        sheet.write(
                            row, pos,
                            str(round(exam.numeric_mark,2)), mark_format)
                        pos += 1
                    competence = self._get_kid_record(
                        student.id, records, competence_line.id)
                    competence_mark = competence.filtered(
                        lambda c: not c.exam_id)
                    competence_mark_mark = competence_mark.calculated_partial_mark if eval_type == 'provisional' else competence_mark.numeric_mark
                    mark_format = self.get_record_format(competence_mark_mark,
                                                         competence_mark.state,
                                                         'competence')
                    sheet.write(
                        row, pos,
                        str(round(competence_mark_mark,2)), mark_format)
                    pos += 1
                eval = self._get_kid_record(student.id, records, eval_line.id)
                eval_mark_mark = eval.calculated_partial_mark if eval_type == 'provisional' else eval.numeric_mark
                mark_format = self.get_record_format(eval_mark_mark,
                                                     eval.state,
                                                     'evaluation')

                sheet.write(row, pos, str(round(eval_mark_mark,2)), mark_format)
                pos += 1

            global_mark = self._get_kid_record(student.id, records, line.id)
            global_mark_mark = global_mark.calculated_partial_mark if eval_type == 'provisional' else global_mark.numeric_mark
            mark_format = self.get_record_format(global_mark_mark,
                                                 global_mark.state,
                                                 'global')
            sheet.write(row, pos, str(round(global_mark_mark,2)), mark_format)
            pos += 1

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        for schedule in objects:
            group_sheet = self.create_schedule_sheet(workbook, schedule)
            row = 7
            for student in schedule.student_ids:
                self.fill_student_row_data(
                    group_sheet, row, student, schedule)
                row += 1

    def _get_kid_record(self, kid_id, schedule_records, n_line_id):
        return schedule_records.filtered(
            lambda r: r.student_id.id == kid_id and r.n_line_id.id == n_line_id)

    def _get_kid_exam_record(self, kid_id, schedule_records, exam_id):
        return schedule_records.filtered(
            lambda r: r.student_id.id == kid_id and r.exam_id.id == exam_id)

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            "doc_ids": docids,
            "doc_model": "education.schedule",
            "docs": self.env['education.schedule'].browse(docids),
            #'report_type': data.get('report_type') if data else '',
        }

    def get_record_format(self, mark, evaluated, eval_type=None,
                          base_format_vals=None):
        if not base_format_vals:
            base_format_vals = self.base_mark_format_vals
        if evaluated == 'assessed':
            base_format_vals = dict(base_format_vals, bold='1')
        if mark < 5:
            base_format_vals = dict(base_format_vals, color="red")
        if eval_type == 'competence':
            base_format_vals = dict(base_format_vals, fg_color="#f2f2f2")
        if eval_type == 'evaluation':
            base_format_vals = dict(base_format_vals, fg_color="#ffffcc")
        if eval_type == 'global':
            base_format_vals = dict(base_format_vals, fg_color="#ccffdd")
        return self.workbook.add_format(base_format_vals)

    def _define_formats(self, workbook):
        self.workbook = workbook
        base_format_vals = {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vjustify",
        }
        self.title_format = workbook.add_format(base_format_vals)
        header_format_vals = dict(base_format_vals, fg_color="#F2F2F2")
        self.header_format = workbook.add_format(header_format_vals)
        self.subheader_format = workbook.add_format(base_format_vals)
        global_format_vals = dict(base_format_vals, fg_color="#4dff88")
        self.global_subheader_format = workbook.add_format(global_format_vals)
        eval_format_vals = dict(base_format_vals, fg_color="#ffff80")
        self.eval_subheader_format = workbook.add_format(eval_format_vals)
        competence_format_vals = dict(base_format_vals, fg_color="#e6e6e6")
        self.competence_subheader_format = workbook.add_format(
            competence_format_vals)
        self.base_mark_format_vals = {
            "border": 1,
            "align": "center",
            "valign": "vjustify",
        }
