# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationClassroom(models.Model):
    _name = 'education.classroom'
    _inherit = 'education.data'
    _description = 'Classroom'

    capacity = fields.Integer(string='Seating Capacity')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        domain=[('education_code', '!=', False)])
