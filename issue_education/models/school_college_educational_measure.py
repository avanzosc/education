# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class SchoolCollegeEducationalMeasure(models.Model):
    _name = 'school.college.educational.measure'
    _description = 'Educational measures'

    name = fields.Char(string='Description', required=True)
    school_id = fields.Many2one(
        comodel_name='res.partner', name='School',
        domain=[('educational_category', '=', 'school')])
    company_id = fields.Many2one(
        comodel_name='res.company', name='Company',
        related='school_id.company_id', store=True)
    severity_level_id = fields.Many2one(
        comodel_name='school.issue.severity.scale', name='Severity level')
