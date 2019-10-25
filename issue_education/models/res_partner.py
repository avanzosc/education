# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = 'res.partner'

    school_issue_ids = fields.One2many(
        string='School Issues', comodel_name='school.issue',
        inverse_name='student_id')
    school_claim_ids = fields.One2many(
        string='School Claims', comodel_name='school.claim',
        inverse_name='student_id')
    school_issue_count = fields.Integer(
        string='School Issue Count', compute='_compute_school_issue_count',
        store=True)
    school_claim_count = fields.Integer(
        string='School Claim Count', compute='_compute_school_claim_count',
        store=True)

    @api.multi
    @api.depends('school_issue_ids')
    def _compute_school_issue_count(self):
        for partner in self.filtered('school_issue_ids'):
            partner.school_issue_count = len(partner.school_issue_ids)

    @api.multi
    @api.depends('school_claim_ids')
    def _compute_school_claim_count(self):
        for partner in self.filtered('school_claim_ids'):
            partner.school_claim_count = len(partner.school_claim_ids)

    @api.multi
    def button_open_school_issues(self):
        self.ensure_one()
        action = self.env.ref('issue_education.action_school_issue')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update({
            'default_student_id': self.id,
        })
        domain = expression.AND([
            [('student_id', 'in', self.ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict

    @api.multi
    def button_open_school_claims(self):
        self.ensure_one()
        action = self.env.ref('issue_education.action_school_claim')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update({
            'default_student_id': self.id,
        })
        domain = expression.AND([
            [('student_id', 'in', self.ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict
