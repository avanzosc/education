# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Resource for Education",
    "version": "12.0.3.0.0",
    "category": "Education",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "resource",
        "education",
    ],
    "data": [
        "views/education_group_view.xml",
        "views/resource_calendar_view.xml",
    ],
    "installable": True,
    "auto_install": True,
    "post_init_hook": "post_init_hook",
}
