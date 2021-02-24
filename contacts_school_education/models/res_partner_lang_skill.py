# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResPartnerLanguageSkill(models.Model):
    _inherit = "res.partner.lang.skill"

    student_current_group_id = fields.Many2one(
        comodel_name="education.group", string="Current Group",
        compute="_compute_group_info", store=True, compute_sudo=True)
    student_current_center_id = fields.Many2one(
        comodel_name="res.partner", string="Current Education Center",
        compute="_compute_group_info", store=True, compute_sudo=True)
    student_current_level_id = fields.Many2one(
        comodel_name="education.level", string="Current Education Level",
        compute="_compute_group_info", store=True, compute_sudo=True)
    student_current_course_id = fields.Many2one(
        comodel_name="education.course", string="Current Course",
        compute="_compute_group_info", store=True, compute_sudo=True)

    @api.multi
    @api.depends("partner_id", "partner_id.educational_category",
                 "partner_id.current_center_id", "partner_id.current_level_id",
                 "partner_id.current_course_id", "partner_id.current_group_id")
    def _compute_group_info(self):
        for lang_skill in self.filtered(
                lambda p: p.partner_id.educational_category == "student"):
            lang_skill.student_current_center_id = (
                lang_skill.partner_id.current_center_id)
            lang_skill.student_current_level_id = (
                lang_skill.partner_id.current_level_id)
            lang_skill.student_current_course_id = (
                lang_skill.partner_id.current_course_id)
            lang_skill.student_current_group_id = (
                lang_skill.partner_id.current_group_id)
