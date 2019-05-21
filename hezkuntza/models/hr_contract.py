# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    ed_center_id = fields.Many2one(
        domain=[('educational_category', '=', 'school')])
