# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerEnrollment(models.Model):
    _name = 'res.partner.enrollment'
    _description = 'Partner Enrollment'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Student',
        domain=[('educational_category', 'in', ('student', 'other'))])
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year')
    course_id = fields.Many2one(
        comodel_name='education.course', string='Course')
    repeating = fields.Boolean(string='Repeating Course')
    will_repeat = fields.Boolean(string='Will Repeat this Course Next Year?')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    enrollment_ids = fields.One2many(
        comodel_name='res.partner.enrollment', inverse_name='partner_id',
        string='Enrollments')
