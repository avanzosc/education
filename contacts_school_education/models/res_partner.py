# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = 'res.partner'

    next_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='school_id',
        string='Next Courses')
    prev_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='next_school_id',
        string='Previous Courses')
    alumni_center_id = fields.Many2one(
        comodel_name='res.partner', string='Last Education Center',
        domain=[('educational_category', '=', 'school')])
    alumni_academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Last Academic Year')
    alumni_member = fields.Boolean(string='Alumni Association Member')
    student_group_ids = fields.Many2many(
        comodel_name='education.group', relation='edu_group_student',
        column1='student_id', column2='group_id', string='Education Groups',
        readonly=True)
    current_group_id = fields.Many2one(
        comodel_name='education.group', string='Current Group')
    current_center_id = fields.Many2one(
        comodel_name='res.partner', string='Current Education Center')
    current_level_id = fields.Many2one(
        comodel_name="education.level", string='Current Education Level')
    current_course_id = fields.Many2one(
        comodel_name='education.course', string='Current Course')
    childs_current_center_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Children\'s Current Education Centers', compute_sudo=True,
        compute='_compute_child_current_group_ids', store=True,
        relation="rel_family_center", column1="family_id", column2="center_id")
    childs_current_course_ids = fields.Many2many(
        comodel_name='education.course',
        string='Children\'s Current Courses', compute_sudo=True,
        compute='_compute_child_current_group_ids', store=True,
        relation="rel_family_course", column1="family_id", column2="course_id")
    classroom_ids = fields.One2many(
        comodel_name="education.classroom", inverse_name="center_id",
        string="Classrooms")
    classroom_count = fields.Integer(
        string="Classroom Count", compute="_compute_classroom_count",
        store=True)
    child_number = fields.Integer(
        string="Child Number",
        help="This field defines the child position over enrollees from the "
             "same family")
    children_number = fields.Integer(
        string="Children Number", compute="_compute_children_number",
        store=True, compute_sudo=True)
    family_child_number = fields.Integer(
        string="Child Number in Family", compute="_compute_child_number",
        store=True, compute_sudo=True)

    @api.multi
    def get_current_group(self, academic_year=False):
        self.ensure_one()
        if self.educational_category != "student":
            raise UserError(_("Only students can have education groups."))
        if not academic_year:
            academic_year = self.env["education.academic_year"].search([
                ("current", "=", True),
            ])
        group = self.student_group_ids.filtered(
            lambda g: g.group_type_id.type == "official" and
            g.academic_year_id == academic_year)[:1]
        return group

    @api.multi
    def update_current_group_id(self):
        for partner in self.filtered(
                lambda p: p.educational_category == "student"):
            group = partner.get_current_group()
            partner.write({
                "current_group_id": group and group.id,
                "current_center_id": group and group.center_id.id,
                "current_level_id": group and group.level_id.id,
                "current_course_id": group and group.course_id.id,
            })

    @api.depends("child_ids", "educational_category",
                 "child_ids.educational_category",
                 "child_ids.current_center_id", "child_ids.current_course_id")
    def _compute_child_current_group_ids(self):
        for partner in self.filtered(
                lambda p: p.educational_category == 'family'):
            children = partner.child_ids.filtered(
                lambda c: c.educational_category == "student")
            partner.childs_current_center_ids = [
                (6, 0, children.mapped("current_center_id").ids)]
            partner.childs_current_course_ids = [
                (6, 0, children.mapped("current_course_id").ids)]

    @api.multi
    @api.depends("classroom_ids")
    def _compute_classroom_count(self):
        for partner in self:
            partner.classroom_count = len(partner.classroom_ids)

    @api.multi
    @api.depends("child_ids", "child_ids.educational_category",
                 "educational_category", "child_ids.old_student",
                 "parent_id", "parent_id.children_number")
    def _compute_children_number(self):
        for partner in self.filtered(
                lambda p: p.educational_category == "family" and p.child_ids):
            children = partner.child_ids.filtered(
                lambda p: p.educational_category == "student" and
                not p.old_student)
            children_number = len(children)
            partner.children_number = children_number
        for child_partner in self.filtered("parent_id"):
            child_partner.children_number = (
                child_partner.parent_id.children_number)

    @api.multi
    @api.depends("parent_id", "parent_id.child_ids", "educational_category",
                 "parent_id.child_ids.educational_category",
                 "old_student", "parent_id.child_ids.old_student",
                 "birthdate_date", "parent_id.child_ids.birthdate_date")
    def _compute_child_number(self):
        for partner in self.filtered(
                lambda p: p.educational_category == "student" and
                not p.old_student):
            num = 0
            for child in partner.parent_id.child_ids.filtered(
                    lambda p: p.educational_category == "student" and
                    not p.old_student and
                    p.birthdate_date).sorted("birthdate_date"):
                num += 1
                if partner == child:
                    break
            partner.family_child_number = num

    @api.multi
    def assign_group(self, group, update=False):
        official_group = (group.group_type_id.type == "official")
        academic_year = group.academic_year_id
        for student in self.filtered(
                lambda p: p.educational_category in ("student", "otherchild")):
            has_official_group = student.student_group_ids.filtered(
                lambda g: g.academic_year_id == academic_year and
                g.group_type_id.type == "official")
            write_data = {}
            if update and official_group:
                write_data.update({
                    "current_group_id": group.id,
                    "current_center_id": group.center_id.id,
                    "current_level_id": group.level_id.id,
                    "current_course_id": group.course_id.id,
                })
            if not has_official_group:
                write_data.update({
                    "student_group_ids": [(4, group.id)],
                })
                student.write(write_data)

    @api.multi
    def action_discontinue(self, date=False):
        self.ensure_one()
        if self.educational_category not in ("student", "otherchild"):
            return
        current_group = self.get_current_group()
        self.write({
            "educational_category": "otherchild",
            "old_student": True,
            "alumni_center_id": current_group.center_id.id,
            "alumni_academic_year_id": current_group.academic_year_id.id,
            "current_center_id": False,
            "current_level_id": False,
            "current_course_id": False,
            "current_group_id": False,
        })
        self.message_post(
            body=_("Student's registration has been discharged."))

    @api.multi
    def button_open_current_student(self):
        self.ensure_one()
        if self.educational_category != "school":
            return
        action = self.env.ref('contacts.action_contacts')
        action_dict = action and action.read()[0]
        domain = expression.AND([
            [("current_center_id", "=", self.id)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def button_open_relative_student(self):
        self.ensure_one()
        if self.educational_category != "family":
            return
        action = self.env.ref("education.action_education_group_report")
        students = self.mapped("family_ids.child2_id")
        academic_year = self.env["education.academic_year"].search([
            ("current", "=", True)])
        action_dict = action and action.read()[0]
        domain = expression.AND([
            [("student_id", "in", students.ids),
             ("academic_year_id", "in", academic_year.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def button_open_classroom(self):
        self.ensure_one()
        if self.educational_category != "school":
            return
        action = self.env.ref("education.action_education_classroom")
        action_dict = action and action.read()[0]
        domain = expression.AND([
            [("center_id", "in", self.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict

    @api.multi
    def get_formview_id(self, access_uid=None):
        """ Return an view id to open the document ``self`` with. This method
            is meant to be overridden in addons that want to give specific view
            ids for example.

            Optional access_uid holds the user that would access the form view
            id different from the current environment user.
        """
        if self.educational_category == "student":
            view_id = self.env.ref(
                "education.res_partner_education_minimal_view_form").id
        elif self.educational_category in (
                "progenitor", "guardian", "otherrelative"):
            view_id = self.env.ref(
                "education."
                "res_partner_education_responsible_minimal_view_form").id
        else:
            view_id = super(ResPartner, self).get_formview_id()
        return view_id
