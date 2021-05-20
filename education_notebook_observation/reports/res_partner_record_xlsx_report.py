# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class EducationGroupXlsx(models.AbstractModel):
    _inherit = "report.education.partner_record_xlsx"

    def __init__(self, pool, cr):
        super().__init__(pool, cr)
        self.format_observations_header = None
        self.format_observations = None

    def fill_student_subject_data(self, sheet, student, subject, row):
        observation_obj = self.env["education.notebook.observation"]
        evaluation_obj = self.env["education.academic_year.evaluation"]
        row = super(EducationGroupXlsx, self).fill_student_subject_data(
            sheet, student, subject, row)
        observations = observation_obj.search([
            ("e_notebook_line_id.a_year_id.current", "=", True),
            ("student_id", "=", student.id),
            ("e_notebook_line_id.subject_id", "=", subject.id),
        ])
        if observations:
            teacher_list = ",".join(observations.mapped(
                "teacher_id.display_name"))
            sheet.merge_range(
                row, 0, row, 6, _("Observations ({})").format(teacher_list),
                self.format_header_center)
            row += 1
            for eval_type in ["first", "second", "third", "final"]:
                eval_observations = observations.filtered(
                    lambda o: o.e_notebook_line_id.eval_type == eval_type)
                for observation in eval_observations:
                    field = evaluation_obj._fields["eval_type"]
                    eval_type_text = field.convert_to_export(
                        eval_type, evaluation_obj)
                    sheet.set_row(row, 170)
                    sheet.write(
                        row, 0, eval_type_text,
                        self.format_observations_header)
                    sheet.merge_range(
                        row, 1, row, 6, observation.observations or _("UN"),
                        self.format_observations)
                    row += 1
        return row

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Those formats can be used on all cell.
        """
        super()._define_formats(workbook)
        self.format_observations = workbook.add_format({
            "border": True,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })
        self.format_observations_header = workbook.add_format({
            "bold": True,
            "bg_color": "#F2F2F2",
            "border": True,
            "align": "center",
            "valign": "top",
            "text_wrap": True,
        })
