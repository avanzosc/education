# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class SchoolIssueProof(models.Model):
    _name = 'school.issue.proof'
    _description = 'Issue Proof'

    name = fields.Char(string='Description', required=True)
    person_id = fields.Many2one(
        comodel_name='res.partner', name='Progenitor/Tutor',
        domain=[('educational_category', 'in', ('progenitor', 'guardian'))])
