# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationGroup(models.Model):
    _inherit = "education.group"

    center_id = fields.Many2one(
        domain=[("educational_category", "=", "school")])
    student_ids = fields.Many2many(
        domain=[("educational_category", "=", "student")])

    @api.depends("student_ids", "student_ids.educational_category")
    def _compute_student_count(self):
        super()._compute_student_count()

    @api.model
    def create(self, values):
        group = super(EducationGroup, self).create(values)
        if group.student_ids:
            group.update_student_current_group_id()
        return group

    @api.multi
    def write(self, values):
        result = super(EducationGroup, self).write(values)
        if "student_ids" in values:
            self.update_student_current_group_id()
        return result

    @api.multi
    def update_student_current_group_id(self):
        official_groups = self.filtered(
            lambda g: g.group_type_id.type == "official")
        official_groups.mapped("student_ids").update_current_group_id()

    @api.multi
    def create_schedule(self):
        teacher = self.env.ref("education.hr_employee_anonymous")
        task_type = self.env.ref(
            "contacts_school_education.education_task_type_0120")
        language = self.env["education.language"].search([], limit=1)
        subject_center_obj = self.env["education.subject.center"]
        schedule_obj = self.env["education.schedule"]
        for group in self.filtered(
                lambda g: g.group_type_id.type == "official" and
                g.course_id):
            subject_center = subject_center_obj.search([
                ("center_id", "=", group.center_id.id),
                ("level_id", "=", group.level_id.id),
                ("course_id", "=", group.course_id.id),
            ])
            for subject in subject_center.mapped("subject_id"):
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
