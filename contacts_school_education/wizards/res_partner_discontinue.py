# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartnerDiscontinue(models.TransientModel):
    _name = "res.partner.discontinue"
    _description = "Wizard for selecting discontinue date"

    date = fields.Date(
        string="Discontinue Date", default=fields.Date.today(), required=True)

    @api.multi
    def discontinue(self):
        context = self.env.context
        if context.get("active_model") == "res.partner":
            partners = self.env["res.partner"].browse(
                context.get("active_ids"))
            for partner in partners:
                partner.action_discontinue(self.date)
        return {'type': 'ir.actions.act_window_close'}
