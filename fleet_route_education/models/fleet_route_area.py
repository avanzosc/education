# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FleetRouteArea(models.Model):
    _name = "fleet.route.area"
    _description = 'Stop areas for fleet routes'

    name = fields.Char("Name")
    education_center_id = fields.Many2one(
        comodel_name='res.partner',
        string='Education Center',
        domain="[('educational_category', '=', 'school')]",
    )


class FleetRouteStop(models.Model):
    _inherit = "fleet.route.stop"

    area_id = fields.Many2one(
        comodel_name='fleet.route.area',
        string='Route Area'
    )
