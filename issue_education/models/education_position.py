# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class EducationPosition(models.Model):
    _inherit = 'education.position'

    issue_level_id = fields.Many2one(
        string='Issue severity level',
        comodel_name='school.issue.serverity.level')
