# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartnerPermission(models.Model):
    _inherit = "res.partner.permission"

    center_id = fields.Many2one(required=True)

    @api.model
    def create(self, values):
        if not values.get('center_id'):
            partner = self.env["res.partner"].browse(values.get("partner_id"))
            values["center_id"] = partner.current_center_id.id
        return super(ResPartnerPermission, self).create(values)
