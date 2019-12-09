# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationBehaviourMark(models.Model):
    _name = 'education.mark.behaviour'
    _description = 'Behaviour Mark'

    name = fields.Char(string='Name')
    code = fields.Selection(selection=[
        ('A', 'Very Good'),
        ('B', 'Good'),
        ('C', 'Normal'),
        ('D', 'Insufficient'),
        ('E', 'Bad'),
        ('F', 'Very Bad')],
        string='Code', default='C', required=True)
