# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import TestFleetRouteEducationCommon
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestFleetRouteEducation(TestFleetRouteEducationCommon):

    def test_partner_current_stop(self):
        stops = self.passenger.current_bus_stop(self.route.direction)
        self.assertIn(stops, self.passenger.mapped("stop_ids.stop_id"))

    def test_partner_current_issue(self):
        issues = self.passenger.current_bus_issues(self.route.direction)
        self.assertEquals(len(issues), 4)
        note_issue = issues.filtered(lambda l: l.type == "note")
        self.assertEquals(self.note_issue, note_issue)
        low_issue = issues.filtered(lambda l: l.type == "low")
        self.assertEquals(self.low_issue, low_issue)
        high_issue = issues.filtered(lambda l: l.type == "high")
        self.assertEquals(self.high_issue, high_issue)
        change_issue = issues.filtered(lambda l: l.type == "change")
        self.assertEquals(self.change_issue, change_issue)

    def test_partner_empty(self):
        self.passenger.write({
            "educational_category": "progenitor",
        })
        stops = self.passenger.current_bus_stop(self.route.direction)
        self.assertFalse(stops)
        issues = self.passenger.current_bus_issues(self.route.direction)
        self.assertFalse(issues)
