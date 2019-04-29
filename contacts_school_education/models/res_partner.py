# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    next_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='school_id')
    prev_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='next_school_id')
