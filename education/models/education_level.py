# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationLevel(models.Model):
    _name = 'education.level'
    _inherit = 'education.data'
    _description = 'Education Level'

    plan_id = fields.Many2one(
        comodel_name='education.plan', string='Plan', required=True,
        ondelete='cascade')
    task_type_ids = fields.Many2many(
        comodel_name='education.task_type', string='Task Types',
        relation='rel_education_level_task_type',
        column1='level_id', column2='task_type_id')
    academic_year_workday_type_id = fields.One2many(
        comodel_name='education.level.workday_type', inverse_name='level_id',
        string='Workday Type per Academic Year')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code,plan_id)',
         'Education code must be unique per plan!'),
    ]

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
            result.append((record.id, '[{}] {} ({})'.format(
                record.education_code, record.description,
                record.plan_id.description)))
        return result
