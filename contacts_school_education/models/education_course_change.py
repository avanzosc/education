# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class EducationCourseChange(models.Model):
    _name = "education.course.change"
    _description = "Course Change"
    _inherit = ['mail.thread']
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
        comodel_name="education.subject", relation="subject_change_rel",
        column1="course_change_id", column2="subject_id",
        string="Next Education Subjects", compute="_compute_next_subject")
    next_subject_count = fields.Integer(
        string="# Subject", compute="_compute_next_subject")
    gender = fields.Selection(
        string="Gender", selection=_get_selection_gender, copy=False)

    @api.multi
    def _get_center_course_subject_list(self):
        self.ensure_one()
        return self.env["education.subject.center"].search([
            ("center_id", "=", self.next_school_id.id),
            ("level_id", "=", self.next_level_id.id),
            ("course_id", "=", self.next_course_id.id),
        ])

    @api.depends("next_school_id", "next_level_id", "next_course_id")
    def _compute_next_subject(self):
        for record in self:
            subject_centers = record._get_center_course_subject_list()
            subjects = subject_centers.mapped("subject_id")
            record.next_subject_ids = [(6, 0, subjects.ids)]
            record.next_subject_count = len(subjects)

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
    def button_open_subject_list(self):
        self.ensure_one()
        action = self.env.ref("education.action_education_subject_center")
        action_dict = action and action.read()[0]
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        action_dict['context'].update({
            "default_center_id": self.next_school_id.id,
            "default_level_id": self.next_level_id.id,
            "default_course_id": self.next_course_id.id,
        })
        domain = expression.AND([
            [("center_id", "=", self.next_school_id.id),
             ("level_id", "=", self.next_level_id.id),
             ("course_id", "=", self.next_course_id.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
