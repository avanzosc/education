# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = "lastname,lastname2,firstname,display_name"

    education_code = fields.Char(string='Education Code', copy=False)
    edu_idtype_id = fields.Many2one(
        comodel_name='education.idtype', string='ID Type')
    education_group_count = fields.Integer(
        string='# Education Groups', compute='_compute_education_group_count')
    timetable_ids = fields.One2many(
        comodel_name="education.group.student.timetable.report",
        inverse_name="student_id")

    _sql_constraints = [
        ('education_code_uniq', 'unique(education_code)',
         'Education code must be unique!'),
    ]

    @api.multi
    def _compute_education_group_count(self):
        group_obj = self.env['education.group']
        for partner in self:
            partner.education_group_count = group_obj.search_count([
                ('center_id', '=', partner.id)])

    @api.multi
    def button_open_education_groups(self):
        self.ensure_one()
        action = self.env.ref('education.action_education_group')
        action_dict = action.read()[0]
        action_dict.update({
            'domain': [('center_id', '=', self.id)],
        })
        return action_dict

    @api.multi
    def get_timetable_max_daily_hour(self):
        self.ensure_one()
        reports = self.timetable_ids.filtered(
            lambda r: r.academic_year_id.current)
        return max(reports.mapped("daily_hour")) if reports else False

    @api.multi
    def get_timetable_info(self, dayofweek, daily_hour):
        self.ensure_one()
        reports = self.timetable_ids.filtered(
            lambda r: r.academic_year_id.current)
        return reports.filtered(
            lambda r: r.dayofweek == str(dayofweek) and
            r.daily_hour == daily_hour)
