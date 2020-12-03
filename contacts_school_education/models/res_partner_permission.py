# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartnerPermission(models.Model):
    _inherit = "res.partner.permission"

    center_id = fields.Many2one(required=True)
    current_group_id = fields.Many2one(
        comodel_name="education.group", string="Student Current Group",
        related="partner_id.current_group_id", store=True)
    current_center_id = fields.Many2one(
        comodel_name="res.partner", string="Student Current Education Center",
        related="partner_id.current_center_id", store=True)
    current_level_id = fields.Many2one(
        comodel_name="education.level",
        string="Student Current Education Level",
        related="partner_id.current_level_id", store=True)
    current_course_id = fields.Many2one(
        comodel_name="education.course", string="Student Current Course",
        related="partner_id.current_course_id", store=True)

    @api.model
    def create(self, values):
        if not values.get("center_id"):
            partner = self.env["res.partner"].browse(values.get("partner_id"))
            values["center_id"] = partner.current_center_id.id
        return super(ResPartnerPermission, self).create(values)
