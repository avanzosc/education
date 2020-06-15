# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class EducationGroup(models.Model):
    _inherit = "education.group"

    @api.multi
    def create_schedule(self):
        teacher = self.env.ref("education.hr_employee_anonymous")
        task_type = self.env.ref(
            "contacts_school_education.education_task_type_0120")
        language = self.env["education.language"].search([], limit=1)
        course_change_obj = self.env["education.course.change"]
        schedule_obj = self.env["education.schedule"]
        for group in self.filtered(
                lambda g: g.group_type_id.type == "official" and
                g.course_id):
            course_change = course_change_obj.search([
                ("next_school_id", "=", group.center_id.id),
                ("next_course_id", "=", group.course_id.id),
            ])
            for subject in course_change.mapped("next_subject_ids"):
                schedule_obj.create({
                    "center_id": group.center_id.id,
                    "teacher_id": teacher.id,
                    "academic_year_id": group.academic_year_id.id,
                    "task_type_id": task_type.id,
                    "classroom_id": group.classroom_id.id,
                    "group_ids": [(4, group.id)],
                    "subject_id": subject.id,
                    "level_id": group.level_id.id,
                    "plan_id": group.plan_id.id,
                    "language_id": language.id,
                })
