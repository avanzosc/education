# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationLevelFieldSubject(models.Model):
    _name = 'education.level.field.subject'
    _description = 'Education Level, Field and Subject Relation'

    level_id = fields.Many2one(
        comodel_name='education.level', string='Level')
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Plan')
    field_id = fields.Many2one(
        comodel_name='education.field', string='Study Field')
    subject_id = fields.Many2one(
        comodel_name='education.subject', string='Subject')
