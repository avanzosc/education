# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrEmployeeEduType(models.Model):
    _name = "hr.employee.edu_type"
    _description = "Employee Education Type"

    name = fields.Char(string="Name", translate=True, required=True)
