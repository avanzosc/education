# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SchoolIssueProof(models.Model):
    _name = 'school.issue.proof'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Issue Proof'

    name = fields.Char(string='Description', required=True)
    student_id = fields.Many2one(
        comodel_name='res.partner', name='Student', required=True,
        domain=[('educational_category', '=', 'student')])
    allowed_partner_ids = fields.Many2many(
        comodel_name='res.partner', relation='rel_proof_progenitor',
        column1='proof_id', column2='progenitor_id',
        compute='_compute_progenitor_ids', store=True)
    person_id = fields.Many2one(
        comodel_name='res.partner', name='Progenitor/Tutor')
    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')
    college_issue_type_id = fields.Many2one(
        comodel_name='school.college.issue.type', string='Issue Type')
    school_id = fields.Many2one(
        comodel_name='res.partner', name='Education Center',
        related='college_issue_type_id.school_id', store=True)
    issue_ids = fields.One2many(
        comodel_name='school.issue', inverse_name='proof_id',
        string='Issues')
    notes = fields.Text(string='Notes')

    @api.depends('student_id', 'student_id.child2_ids',
                 'student_id.child2_ids.relation',
                 'student_id.child2_ids.responsible_id')
    def _compute_progenitor_ids(self):
        for proof in self:
            proof.allowed_partner_ids = proof.student_id.child2_ids.filtered(
                lambda f: f.relation == 'progenitor').mapped('responsible_id')
