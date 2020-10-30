# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    timetable_ids = fields.One2many(
        comodel_name="education.group.teacher.timetable.report",
        inverse_name="professor_id")

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

    @api.multi
    def button_open_schedule(self):
        self.ensure_one()
        action = self.env.ref(
            "education.action_education_group_teacher_timetable_report")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("professor_id", "=", self.id)],
            safe_eval(action.domain or "[]")
        ])
        action_dict.update({
            "domain": domain,
        })
        return action_dict
