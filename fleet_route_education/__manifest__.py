# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Fleet Route Education",
    "version": "12.0.1.0.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "fleet_route_school",
        "contacts_school_education",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/fleet_route_education_security.xml",
        "reports/res_partner_fleet_route_report_view.xml",
        "views/fleet_route_stop_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
