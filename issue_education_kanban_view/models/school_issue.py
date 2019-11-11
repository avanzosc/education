# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class SchoolIssue(models.Model):
    _inherit = 'school.issue'

    def create_issue_name(self, student, school_issue_type, schedule=False):
        student = student or self.student_id
        school_issue_type = school_issue_type or self.school_issue_type_id
        schedule = schedule or self.education_schedule_id
        name = _('Student: {}, Issue type: {}').format(
            student.display_name, school_issue_type.name)
        if schedule:
            name = _('{}, Education subject: {}').format(
                name, schedule.subject_id.description or
                schedule.task_type_id.description)
        return name
