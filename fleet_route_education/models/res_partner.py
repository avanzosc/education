# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def current_bus_stop(self, direction):
        self.ensure_one()
        if (not direction or direction not in ("going", "coming") or
                self.educational_category != "student"):
            return
        today = fields.Date.context_today(self)
        stop_passenger = self.stop_ids.filtered(
            lambda s: s.stop_id.route_id.direction == direction and
            ((s.start_date and (s.start_date <= today)) or
             not s.start_date) and
            ((s.end_date and (s.end_date >= today)) or not s.end_date))[:1]
        return stop_passenger.stop_id or False

    def current_bus_issues(self, direction):
        self.ensure_one()
        if (not direction or direction not in ("going", "coming") or
                self.educational_category != "student"):
            return
        today = fields.Date.context_today(self)
        stop_issues = self.bus_issue_ids.filtered(
            lambda i: i.date == today and ((
                i.low_stop_id.route_id.direction == direction or
                i.high_stop_id.route_id.direction == direction) or
                i.type == 'note'))
        return stop_issues
