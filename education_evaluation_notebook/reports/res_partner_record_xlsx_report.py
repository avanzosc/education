# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class EducationGroupXlsx(models.AbstractModel):
    _name = "report.education.partner_record_xlsx"
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
        self.format_border_grey = None
        self.format_bold = None
        self.format_italic = None
        self.format_left = None
        self.format_header_center = None
        self.format_header_right = None
        self.format_amount = None
        self.format_amount_grey = None

    def _get_not_passed(self):
        return [
            self.env.ref(
                "education_evaluation_notebook.numeric_mark_insufficient"),
            self.env.ref(
                "education_evaluation_notebook.numeric_mark_very_bad")]

    def create_student_sheet(self, workbook, student):
        sheet = workbook.add_worksheet(student.display_name)
        sheet.merge_range("A1:C1", _("Student:"), self.format_header_right)
        sheet.merge_range("D1:G1", student.display_name, self.format_left)
        sheet.merge_range(
            "A2:C2", _("Education Center:"), self.format_header_right)
        sheet.merge_range(
            "D2:G2", student.current_center_id.display_name, self.format_left)
        sheet.merge_range(
            "A3:C3", _("Education Course:"), self.format_header_right)
        sheet.merge_range(
            "D3:G3", student.current_course_id.display_name, self.format_left)
        sheet.merge_range(
            "A4:C4", _("Education Group:"), self.format_header_right)
        sheet.merge_range(
            "D4:G4", student.current_group_id.display_name, self.format_left)
        sheet.merge_range(
            "A5:C5", _("Tutor:"), self.format_header_right)
        sheet.merge_range(
            "D5:G5", student.current_year_tutor_ids[:1].display_name,
            self.format_left)

        sheet.set_column("A:G", 10)
        return sheet

    def set_evaluation_header_table(self, sheet, row):
        sheet.write(row, 3, "Primera", self.format_header_center)
        sheet.write(row, 4, "Segunda", self.format_header_center)
        sheet.write(row, 5, "Tercera", self.format_header_center)
        sheet.write(row, 6, "Final", self.format_header_center)

    def write_evaluation_mark(self, sheet, row, eval_type, data, format):
        if eval_type == "first":
            column = 3
        elif eval_type == "second":
            column = 4
        elif eval_type == "third":
            column = 5
        elif eval_type == "final":
            column = 6
        else:
            return False
        sheet.write(row, column, data, format)

    def fill_student_subject_data(self, sheet, student, subject, row):
        self.set_evaluation_header_table(sheet, row)
        record_obj = self.env["education.record"]
        domain = [
            ("student_id", "=", student.id),
            ("subject_id", "=", subject.id),
        ]
        records = record_obj.search(domain)
        row += 1
        sheet.merge_range(
            row, 0, row, 2, subject.display_name, self.format_bold)
        for record in records.filtered(
                lambda r: r.evaluation_competence or r.global_competence):
            sheet.set_row(row, None, self.format_border)
            self.write_evaluation_mark(
                sheet, row, record.eval_type, record.numeric_mark,
                self.format_amount)
        row += 1
        for record in records.filtered(
                lambda r: not r.evaluation_competence and
                not r.global_competence and not r.exam_id):
            sheet.set_row(row, None, self.format_border)
            sheet.merge_range(
                row, 0, row, 2, record.n_line_id.description,
                self.format_border_grey)
            self.write_evaluation_mark(
                sheet, row, record.eval_type, record.numeric_mark,
                self.format_amount_grey)
            row += 1
            for exam_record in record.child_record_ids:
                sheet.set_row(row, None, self.format_border)
                sheet.merge_range(
                    row, 0, row, 2, exam_record.exam_id.display_name,
                    self.format_italic)
                self.write_evaluation_mark(
                    sheet, row, exam_record.eval_type,
                    exam_record.numeric_mark, self.format_amount)
                row += 1
        return row

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        students = []
        if objects._name == "res.partner":
            students = objects
        elif objects._name == "hr.employee.supervised.year":
            students = objects.mapped("student_id")
        record_obj = self.env["education.record"]
        current_academic_year = self.env["education.academic_year"].search([
            ("current", "=", True),
        ])
        academic_year_id = data and data.get(
            "academic_year_id", False) or current_academic_year[:1].id
        # partial_mark = data and data.get("partial_mark", False)
        # retaken = data and data.get("retaken", False)
        if not students:
            raise UserError(
                _("You must select at least one student."))
        if len(students) > 1:
            raise UserError(
                _("Please select only one student"))
        if not academic_year_id:
            raise UserError(
                _("There is no academic year selected."))
        for student in students:
            student_sheet = self.create_student_sheet(workbook, student)
            row = 6
            student_records = record_obj.sudo().search([
                ("student_id", "in", student.ids),
                ("n_line_id.schedule_id.task_type_id.education_code", "!=",
                 "0123"),
                ("n_line_id.schedule_id.academic_year_id", "=",
                 academic_year_id),
            ])
            subject_lists = student_records.mapped("subject_id")
            for subject in subject_lists:
                row = self.fill_student_subject_data(
                    student_sheet, student, subject, row)
                row += 1

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Those formats can be used on all cell.
        """
        self.format_border = workbook.add_format({
            'border': True,
            'align': 'center',
        })
        self.format_border.set_text_wrap()
        border_grey = {
            'border': True,
            'bg_color': '#C0C0C0',
        }
        self.format_border_grey = workbook.add_format(border_grey)
        self.format_border_grey.set_align("center")
        self.format_border_grey.set_text_wrap()
        self.format_bold = workbook.add_format({
            'bold': True,
            'border': True,
            'align': 'center',
        })
        self.format_italic = workbook.add_format({
            'italic': True,
            'border': True,
            'align': 'center',
        })
        self.format_left = workbook.add_format({
            'border': True,
            'align': 'left',
        })
        header_dict = {
            'bold': True,
            'border': True,
            'bg_color': '#F2F2F2'
        }
        self.format_header_center = workbook.add_format(header_dict)
        self.format_header_center.set_align('center')
        self.format_header_right = workbook.add_format(header_dict)
        self.format_header_right.set_align('right')
        self.format_amount = workbook.add_format({'border': True})
        self.format_amount.set_num_format('#,##0.' + '00')
        self.format_amount_grey = workbook.add_format(border_grey)
        self.format_amount_grey.set_num_format('#,##0.' + '00')
