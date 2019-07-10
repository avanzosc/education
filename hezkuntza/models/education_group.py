# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationGroup(models.Model):
    _inherit = 'education.group'

    center_id = fields.Many2one(
        domain=[('educational_category', '=', 'school')])
    student_ids = fields.Many2many(
        domain=[('educational_category', '=', 'student')])
