# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FleetRouteStopPassenger(models.Model):
    _inherit = "fleet.route.stop.passenger"

    partner_group_id = fields.Many2one(
        comodel_name="education.group", string="Current Group",
        related="partner_id.current_group_id", store=True)
    partner_center_id = fields.Many2one(
        comodel_name="res.partner", string="Current Education Center",
        related="partner_id.current_center_id", store=True)
    partner_course_id = fields.Many2one(
        comodel_name="education.course", string="Current Course",
        related="partner_id.current_course_id", store=True)
