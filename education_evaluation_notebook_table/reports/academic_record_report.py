
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.education_evaluation_notebook.models.\
    education_academic_year_evaluation import EVAL_TYPE

_logger = logging.getLogger(__name__)


class AcademicRecordReport(models.AbstractModel):
    _name = "report.education_schedule.academic_record_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def __init__(self, pool, cr):
        self.sheet = None
        self.workbook = None
        # self.schedule = None
        self.eval_type = None
        self.mark_type = None
        self.title_format = None
        self.header_format = None
        self.subheader_format = None
        self.global_subheader_format = None
        self.eval_subheader_format = None
        self.competence_subheader_format = None
        self.base_mark_format_vals = None

    def paint_exam_record_line(self, sheet, row, col, parent_line):
        for exam_line in parent_line.exam_ids:
            sheet.write(row, col,
                        exam_line.display_name,
                        self.subheader_format)
            sheet.set_column(row, col, 10)
            col += 1
        return col

    def paint_record_line(self, sheet, row, col, parent_line):
        col = self.paint_exam_record_line(sheet, row, col, parent_line)
        sheet.write(row, col,
                    parent_line.display_name,
                    self.get_record_line_format(parent_line))
        sheet.set_column(row, col, 20)
        col += 1
        return col

    def create_schedule_sheet(self, workbook, schedule):
        sheet = workbook.add_worksheet(
            "{} {}".format(schedule.classroom_id.display_name, schedule.display_name))

        record_lines = schedule.record_ids.mapped('n_line_id')
        if record_lines and self.eval_type not in ('final', 'reduced_final'):
            record_lines = record_lines.filtered(
                lambda r: r.eval_type == self.eval_type)

        if self.eval_type == 'reduced_final':
            max_range = len(record_lines.filtered(
                lambda r: r.competence_id.global_check or
                r.competence_id.evaluation_check))
        else:
            max_range = len(record_lines) + len(schedule.exam_ids.filtered(
                lambda e: e.eval_type == self.eval_type))

        sheet.merge_range(
            0, 0, 0, max_range, _("SCHEDULE ACADEMIC RECORDS"),
            self.title_format)
        sheet.merge_range("A2:B2", _("Education Center:"), self.header_format)
        sheet.merge_range(
            1, 2, 1, max_range, schedule.center_id.display_name,
            self.subheader_format)
        sheet.merge_range("A3:B3", _("Academic Year:"), self.header_format)
        sheet.merge_range(
            2, 2, 2, max_range, schedule.academic_year_id.display_name,
            self.subheader_format)
        sheet.merge_range("A4:B4", _("Classroom"), self.header_format)
        sheet.merge_range(
            3, 2, 3, max_range, schedule.classroom_id.description,
            self.subheader_format)
        sheet.merge_range(
            4, 0, 4, max_range, schedule.display_name + '[%s]' % dict(EVAL_TYPE).get(
                self.eval_type), self.header_format)

        sheet.write("A7", _("Student"), self.subheader_format)

        if self.eval_type in ('final', 'reduced_final'):
            parent_lines = record_lines.filtered(
                lambda r: r.competence_id.global_check)
        else:
            parent_lines = record_lines.filtered(
                lambda r: r.competence_id.evaluation_check)

        for line in parent_lines:
            pos = 1
            for child_line in record_lines.filtered(
                    lambda r: r.parent_line_id.id == line.id):
                if self.eval_type != 'reduced_final':
                    for child_child_line in record_lines.filtered(
                            lambda r: r.parent_line_id.id == child_line.id):
                        pos = self.paint_record_line(
                            sheet, 6, pos, child_child_line)

                pos = self.paint_record_line(sheet, 6, pos, child_line)

            pos = self.paint_record_line(sheet, 6, pos, line)

        sheet.set_column("A:A", 35)
        return sheet

    def paint_exam_record_mark(self, sheet, row, col, parent_record, student):
        for exam in parent_record.exam_ids:
            exam_record = self._get_kid_exam_record(exam, student)
            mark_format = self.get_record_format(
                exam_record.numeric_mark, exam_record.state)
            sheet.write(
                row, col,
                str(round(exam_record.numeric_mark, 2)), mark_format)
            col += 1
        return col

    def paint_record_mark(self, sheet, row, col, parent_record_line, student):
        col = self.paint_exam_record_mark(
            sheet, row, col, parent_record_line, student)
        current_record = self._get_kid_record(parent_record_line, student)
        current_record_mark = current_record.calculated_partial_mark if\
            self.mark_type == 'provisional' else current_record.numeric_mark
        mark_record_type = self.get_mark_eval_type(parent_record_line)
        mark_format = self.get_record_format(
            current_record_mark, current_record.state, mark_record_type)
        sheet.write(
            row, col,
            str(round(current_record_mark, 2)), mark_format)
        col += 1
        return col

    def get_mark_eval_type(self, record_line):
        competence = record_line.competence_id
        record_type = None
        if competence.global_check:
            record_type = 'global'
        if competence.evaluation_check:
            record_type = 'evaluation'
        if not competence.global_check and not competence.evaluation_check:
            record_type = 'competence'
        return record_type

    def fill_student_row_data(
            self, sheet, row, student, schedule):
        sheet.write(row, 0, student.name)

        records = schedule.record_ids
        record_lines = records.mapped('n_line_id')
        if record_lines and self.eval_type not in ('final', 'reduced_final'):
            record_lines = record_lines.filtered(
                lambda r: r.eval_type == self.eval_type)

        if self.eval_type in ('final', 'reduced_final'):
            parent_lines = record_lines.filtered(
                lambda r: r.competence_id.global_check)
        else:
            parent_lines = record_lines.filtered(
                lambda r: r.competence_id.evaluation_check)

        for line in parent_lines:
            pos = 1
            for child_line in record_lines.filtered(
                    lambda r: r.parent_line_id.id == line.id):
                if self.eval_type != 'reduced_final':
                    for child_child_line in record_lines.filtered(
                            lambda r: r.parent_line_id.id == child_line.id):
                        pos = self.paint_record_mark(
                            sheet, row, pos, child_child_line, student)

                pos = self.paint_record_mark(sheet, row, pos, child_line,
                                             student)

            pos = self.paint_record_mark(
                sheet, row, pos, line, student)

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        if not objects:
            raise UserError(
                _("You can only get xlsx report of education schedules"))
        self.eval_type = data and data.get("eval_type", False)
        self.mark_type = data and data.get("mark_type", False)
        for schedule in objects:
            group_sheet = self.create_schedule_sheet(
                workbook, schedule)
            row = 7
            for student in schedule.student_ids:
                self.fill_student_row_data(
                    group_sheet, row, student, schedule)
                row += 1

    def _get_kid_record(self, n_line, kid):
        return n_line.record_ids.filtered(
            lambda r: r.student_id == kid and not r.exam_id and
            not r.recovered_record_id)

    def _get_kid_exam_record(self, exam, kid):
        return exam.record_ids.filtered(
            lambda r: r.student_id == kid)

    def get_record_line_format(self, record_line):
        format_vals = self.subheader_format
        record_type = self.get_mark_eval_type(record_line)
        if record_type == 'global':
            format_vals = self.global_subheader_format
        if record_type == 'evaluation':
            format_vals = self.eval_subheader_format
        if record_type == 'competence':
            format_vals = self.competence_subheader_format
        return format_vals

    def get_record_format(self, mark, evaluated, record_type=None,
                          base_format_vals=None):
        if not base_format_vals:
            base_format_vals = self.base_mark_format_vals
        if evaluated == 'assessed':
            base_format_vals = dict(base_format_vals, bold='1')
        if mark < 5:
            base_format_vals = dict(base_format_vals, color="red")
        if record_type == 'competence':
            base_format_vals = dict(base_format_vals, fg_color="#f2f2f2")
        if record_type == 'evaluation':
            base_format_vals = dict(base_format_vals, fg_color="#ffffcc")
        if record_type == 'global':
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
        subheader_format_vals = dict(base_format_vals, valign='sideways')
        self.subheader_format = workbook.add_format(subheader_format_vals)
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
