# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationPlan(models.Model):
    _name = 'education.plan'
    _inherit = 'education.data'
    _description = 'Education Plan'

    level_ids = fields.One2many(
        comodel_name='education.level', string='Levels',
        inverse_name='plan_id')
    course_ids = fields.One2many(
        comodel_name='education.course', string='Courses',
        inverse_name='plan_id')

    _sql_constraints = [
        ('education_code_unique', 'unique(education_code)',
         'Education code must be unique!'),
    ]

    @api.multi
    def write(self, vals):
        res = super(EducationPlan, self).write(vals) if vals else True
        if 'active' in vals:
            # archiving/unarchiving a plan does it on its levels, too
            self.with_context(active_test=False).mapped('level_ids').write(
                {'active': vals['active']})
        if 'active' in vals:
            # archiving/unarchiving a plan does it on its levels, too
            self.with_context(active_test=False).mapped('course_ids').write(
                {'active': vals['active']})
        return res
