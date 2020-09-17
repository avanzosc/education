# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.fleet_route_contract.tests.common import \
    FleetRouteContractCommon


class FleetRouteContractEducationCommon(FleetRouteContractCommon):

    @classmethod
    def setUpClass(cls):
        super(FleetRouteContractEducationCommon, cls).setUpClass()
        cls.passenger_report = cls.env["res.partner.fleet.route.report"]
