# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models
from odoo.models import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    student_issue_ids = fields.One2many(
        string='Student issues', comodel_name='student.issue',
        compute='_compute_student_issue_ids', compute_sudo=True)

    def _compute_student_issue_ids(self):
        context = self.env.context
        for student in self:
            cond = []
            school_id = context.get('school_id', student.current_center_id.id)
            schedule_id = context.get('education_schedule_id', False)
            # group_id = context.get('education_group_id', False)
            if school_id:
                classroom_site = self.env.ref(
                    'issue_education.classroom_school_issue_site')
                cond = [('affect_to', '=', 'student'),
                        ('school_id', '=', school_id)]
                level_id = student.current_course_id.level_id
                level_cond = [("education_level_id", "=", False)]
                if level_id:
                    level_cond = expression.OR([
                        [("education_level_id", "=", level_id.id)],
                        level_cond])
                cond = expression.AND([level_cond, cond])
                if schedule_id and classroom_site:
                    cond = expression.AND([
                        ["|", ("issue_type_id.site_id", "=", False),
                         ("issue_type_id.site_id", '=', classroom_site.id)],
                        cond])
            issue_types = self.env['school.college.issue.type']
            if cond:
                issue_types = issue_types.search(cond, order='sequence')
            student_issues = self.env['student.issue']
            for issue_type in issue_types:
                student_issue_vals = {
                    'student_id': student.id,
                    'education_schedule_id': schedule_id,
                    'college_issue_type_id': issue_type.id,
                }
                student_issues |= student_issues.create(student_issue_vals)
            student.student_issue_ids = [(6, 0, student_issues.ids)]
