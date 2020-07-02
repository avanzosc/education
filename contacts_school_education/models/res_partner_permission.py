# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerPermission(models.Model):
    _inherit = "res.partner.permission"

    center_id = fields.Many2one(required=True)
