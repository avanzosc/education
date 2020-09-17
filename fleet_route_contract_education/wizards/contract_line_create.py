# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ContractLineCreate(models.TransientModel):
    _inherit = "contract.line.create"

    @api.model
    def default_get(self, fields):
        res = super(ContractLineCreate, self).default_get(fields)
        if (self.env.context.get("active_model") ==
                "res.partner.fleet.route.report"):
            passengers = self.env["res.partner.fleet.route.report"].browse(
                self.env.context.get("active_ids"))
            partners = passengers.mapped("student_id")
            res.update({
                "student_ids": [(6, 0, partners.ids)],
            })
        return res
