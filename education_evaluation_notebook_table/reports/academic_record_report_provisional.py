
import logging
import string
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AcademicRecordReport(models.AbstractModel):
    _name = "report.education_schedule.academic_record_provisional"
    _inherit = "report.education_schedule.academic_record"

    def generate_xlsx_report(self, workbook, data, objects):
        for schedule in objects:
            group_sheet = self.create_schedule_sheet(workbook, schedule)
            row = 8
            for student in schedule.student_ids:
                self.fill_student_row_data(
                    group_sheet, row, student, schedule, 'provisional')
                row += 1
