# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.addons.fleet_route_school.tests.common import\
    TestFleetRouteSchoolCommon


class TestFleetRouteEducationCommon(TestFleetRouteSchoolCommon):

    @classmethod
    def setUpClass(cls):
        super(TestFleetRouteEducationCommon, cls).setUpClass()
        cls.issue_model = cls.env["fleet.route.support"]
        cls.note_issue = cls.issue_model.create({
            "student_id": cls.passenger.id,
            "date": fields.Date.today(),
            "type": "note",
            "notes": "NOTE TEXT",
        })
        cls.low_issue = cls.issue_model.create({
            "student_id": cls.passenger.id,
            "date": fields.Date.today(),
            "type": "low",
            "low_stop_id": cls.stop1.id,
        })
        cls.high_issue = cls.issue_model.create({
            "student_id": cls.passenger.id,
            "date": fields.Date.today(),
            "type": "high",
            "high_stop_id": cls.stop2.id,
        })
        cls.change_issue = cls.issue_model.create({
            "student_id": cls.passenger.id,
            "date": fields.Date.today(),
            "type": "change",
            "low_stop_id": cls.stop1.id,
            "high_stop_id": cls.stop3.id,
        })
