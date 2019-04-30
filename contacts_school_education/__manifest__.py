# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "School Education",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "education",
        "contacts_school",
        "partner_contact_gender",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/education_course_change_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
