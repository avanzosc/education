# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationLevelFieldSubject(models.Model):
    _name = 'education.level.field.subject'
    _description = 'Education Level, Field and Subject Relation'
    _order = 'level_id,field_id,subject_id'

    level_id = fields.Many2one(
        comodel_name='education.level', string='Education Level')
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Education Plan')
    field_id = fields.Many2one(
        comodel_name='education.field', string='Study Field')
    subject_id = fields.Many2one(
        comodel_name='education.subject', string='Subject')
    active = fields.Boolean(compute="_compute_active", store=True)

    @api.multi
    @api.depends(
        "level_id", "level_id.active", "plan_id", "plan_id.active",
        "field_id", "field_id.active", "subject_id", "subject_id.active")
    def _compute_active(self):
        for record in self:
            record.active = (
                (not record.level_id or
                 (record.level_id and record.level_id.active)) and
                (not record.plan_id or
                 (record.plan_id and record.plan_id.active)) and
                (not record.field_id or
                 (record.field_id and record.field_id.active)) and
                (not record.subject_id or
                 (record.subject_id and record.subject_id.active)))
