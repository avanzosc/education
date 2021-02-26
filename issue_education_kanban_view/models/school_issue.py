# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


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

    def _find_today_issue(
            self, student_id, issue_type_id, group_id, schedule_id):
        today = fields.Date.context_today(self)
        cond = [
            ('issue_date', '=', today),
            ('student_id', '=', student_id),
            ('school_issue_type_id', '=', issue_type_id),
            ('group_id', '=', group_id),
            ('education_schedule_id', '=', schedule_id)]
        return self.search(cond, limit=1)

    def prepare_issue_vals(
            self, school_issue_type, student, schedule, group=False):
        today = fields.Date.context_today(self)
        name = self.create_issue_name(
            student, school_issue_type, schedule)
        if not group and schedule:
            group = schedule.group_ids.filtered(
                lambda g: student in g.student_ids)[:1]
        vals = {
            'name': name,
            'school_id': school_issue_type.school_id.id,
            'school_issue_type_id': school_issue_type.id,
            'issue_type_id': school_issue_type.issue_type_id.id,
            'requires_justification':
            school_issue_type.issue_type_id.requires_justification,
            'affect_to': school_issue_type.issue_type_id.affect_to,
            'student_id': student.id,
            'student_group_id': student.current_group_id.id,
            'reported_id': self.env.user.id,
            'issue_date': today,
            'education_schedule_id': schedule.id,
            'group_id': group and group.id,
            'site_id': school_issue_type.issue_type_id.site_id.id,
        }
        return vals
