# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationLevelFieldSubject(models.Model):
    _name = 'education.level.course.subject'
    _description = 'Education Level, Course and Subject Relation'

    level_id = fields.Many2one(
        comodel_name='education.level', string='Education Level')
    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Education Plan')
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course')
    subject_id = fields.Many2one(
        comodel_name='education.subject', string='Subject')
    active = fields.Boolean(compute="_compute_active", store=True)

    @api.multi
    @api.depends(
        "level_id", "level_id.active", "plan_id", "plan_id.active",
        "course_id", "course_id.active", "subject_id", "subject_id.active")
    def _compute_active(self):
        for record in self:
            record.active = (
                (not record.level_id or
                 (record.level_id and record.level_id.active)) and
                (not record.plan_id or
                 (record.plan_id and record.plan_id.active)) and
                (not record.course_id or
                 (record.course_id and record.course_id.active)) and
                (not record.subject_id or
                 (record.subject_id and record.subject_id.active)))

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            result.append((record.id, '{}{}{}{}'.format(
                record.level_id.education_code, record.plan_id.education_code,
                record.course_id.education_code,
                record.subject_id.education_code)))
        return result
