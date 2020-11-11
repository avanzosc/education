# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def current_bus_stop(self, direction, date=False):
        self.ensure_one()
        if (not direction or direction not in ("going", "coming") or
                self.educational_category != "student"):
            return
        if not date:
            date = fields.Date.context_today(self)
        weekday = str(date.weekday())
        stop_passenger = self.stop_ids.filtered(
            lambda p: (
                p.route_id.direction == direction and
                ((((p.start_date and (p.start_date <= date)) or
                    not p.start_date) and
                  ((p.end_date and (p.end_date >= date)) or
                    not p.end_date)) and
                 (not p.dayofweek_ids or
                  (weekday in p.dayofweek_ids.mapped("dayofweek"))))))[:1]
        return stop_passenger.stop_id or False

    def current_bus_issues(self, direction, date=False):
        self.ensure_one()
        if (not direction or direction not in ("going", "coming") or
                self.educational_category != "student"):
            return
        if not date:
            date = fields.Date.context_today(self)
        stop_issues = self.bus_issue_ids.filtered(
            lambda i: i.date == date and ((
                i.low_stop_id.route_id.direction == direction or
                i.high_stop_id.route_id.direction == direction) or
                i.type == 'note'))
        return stop_issues
