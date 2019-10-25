# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SchoolCollegeIssueType(models.Model):
    _name = 'school.college.issue.type'
    _description = 'Types of issues for colleges'
    _order = 'company_id, school_id, sequence'

    @api.model
    def _get_selection_affect_to(self):
        return self.env['resource.calendar.attendance'].fields_get(
            allfields=['dayofweek'])['dayofweek']['selection']

    name = fields.Char(string='Description', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.issue.type', required=True)
    affect_to = fields.Selection(
        string='Affect to', related='issue_type_id.affect_to', store=True,
        selection='_get_selection_affect_to')
    gravity_scale_id = fields.Many2one(
        string='Severity scale', comodel_name='school.issue.severity.scale',
        related='issue_type_id.gravity_scale_id', store=True)
    education_level_id = fields.Many2one(
        string='Level', comodel_name='education.level')
    school_id = fields.Many2one(
        comodel_name='res.partner', name='School',
        domain=[('educational_category', '=', 'school')],
        required=True)
    company_id = fields.Many2one(
        comodel_name='res.company', name='Company',
        related='school_id.company_id', store=True)
    educational_measure_ids = fields.Many2many(
        comodel_name='school.college.educational.measure',
        string='Educational measures', column1='school_issue_type_id',
        column2='school_educational_measure_id',
        relation='rel_school_issue_type_educational_measure')
    notify_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Notify to', column1='school_issue_type_id',
        column2='partner_id',
        relation='rel_school_issue_type_partner')
    image = fields.Binary(string='Image', attachment=True)

    @api.onchange('issue_type_id')
    def onchange_issue_type_id(self):
        self.ensure_one()
        if self.issue_type_id:
            self.name = self.issue_type_id.name
            self.image = self.issue_type_id.image

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 '{}  ({})'.format(record.name,
                                   record.gravity_scale_id.name)))
        return result
