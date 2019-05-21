# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    ed_position_id = fields.Many2one(
        comodel_name='education.position', string='Position',
        domain=[('type', '=', 'normal')])
    ed_position2_id = fields.Many2one(
        comodel_name='education.position', string='Position 2',
        domain=[('type', '=', 'normal')])
    ed_otherposition_id = fields.Many2one(
        comodel_name='education.position', string='Other Position',
        domain=[('type', '=', 'other')])
    ed_designation_id = fields.Many2one(
        comodel_name='education.designation_level', string='Designation Level')
    ed_work_reason_id = fields.Many2one(
        comodel_name='education.work_reason', string='Work Reason')
    ed_contract_type_id = fields.Many2one(
        comodel_name='education.contract_type', string='Contract Type')
    ed_workday_type_id = fields.Many2one(
        comodel_name='education.workday_type', string='Workday Type')
    ed_work_hours = fields.Float(string='Total Hours')
    ed_class_hours = fields.Float(string='Class Hours')
    ed_contract_hours = fields.Float(string='Contract Hours')
    ed_center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center')
    ed_academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year')
    ed_reduction_health = fields.Boolean(
        string='Reduction for health reasons')
    ed_reduction_age = fields.Boolean(
        string='Reduction for being over 60 years old')
