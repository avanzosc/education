# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationCourseChange(models.Model):
    _name = "education.course.change"
    _description = "Course Change"
    _order = "school_id,course_id,next_school_id,next_course_id,gender"

    @api.model
    def _get_selection_gender(self):
        return self.env["res.partner"].fields_get(
            allfields=["gender"])["gender"]["selection"]

    school_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain=[("educational_category", "=", "school")])
    course_id = fields.Many2one(
        comodel_name="education.course", string="Course")
    level_id = fields.Many2one(
        comodel_name="education.level", string="Education Level",
        related="course_id.level_id")
    field_id = fields.Many2one(
        comodel_name="education.field", string="Study Field",
        related="course_id.field_id")
    plan_id = fields.Many2one(
        comodel_name="education.plan", string="Education Plan",
        related="course_id.plan_id")
    next_school_id = fields.Many2one(
        comodel_name="res.partner", string="Next Education Center",
        domain=[("educational_category", "=", "school")], copy=False)
    next_course_id = fields.Many2one(
        comodel_name="education.course", string="Next Course", copy=False)
    next_level_id = fields.Many2one(
        comodel_name="education.level", string="Next Education Level",
        related="next_course_id.level_id")
    next_field_id = fields.Many2one(
        comodel_name="education.field", string="Next Study Field",
        related="next_course_id.field_id")
    next_plan_id = fields.Many2one(
        comodel_name="education.plan", string="Next Education Plan",
        related="next_course_id.plan_id")
    next_subject_ids = fields.Many2many(
        comodel_name="education.subject", string="Next Education Subjects")
    gender = fields.Selection(
        string="Gender", selection=_get_selection_gender, copy=False)

    @api.constrains("course_id", "next_course_id")
    def _check_different_course(self):
        for record in self:
            if record.course_id == record.next_course_id:
                raise ValidationError(_("Courses must be different."))

    @api.constrains(
        "school_id", "course_id", "next_school_id", "next_course_id", "gender")
    def _check_course_change_unique(self):
        for record in self:
            results = self.search_count([
                ("school_id", "=", record.school_id.id),
                ("course_id", "=", record.course_id.id),
                ("next_school_id", "=", record.next_school_id.id),
                ("next_course_id", "=", record.next_course_id.id),
                ("gender", "=", record.gender),
                ("id", "!=", record.id),
            ])
            if results:
                raise ValidationError(_("Duplicated course change!"))

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            result.append((record.id, "{} ({}) - {} ({})".format(
                record.course_id.description, record.school_id.display_name,
                record.next_course_id.description,
                record.next_school_id.display_name)))
        return result

    @api.multi
    def button_add_subject_list(self):
        group_obj = self.env["education.group"]
        for record in self.filtered(
                lambda r: r.next_school_id and r.next_course_id):
            edu_groups = group_obj.search([
                ("academic_year_id.current", "=", True),
                ("center_id", "=", record.next_school_id.id),
                ("course_id", "=", record.next_course_id.id),
                ("level_id", "=", record.next_course_id.level_id.id),
            ])
            subjects = edu_groups.mapped("schedule_ids.subject_id").filtered(
                lambda s: s.level_ids == record.next_course_id.level_id and
                s.course_ids == record.next_course_id)
            if record.next_course_id.field_id:
                subjects = subjects.filtered(
                    lambda s: s.field_ids == record.next_course_id.field_id or
                    not s.field_ids)
            record.next_subject_ids = [(6, 0, subjects.ids)]
