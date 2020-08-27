# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Human Resources for Education",
    "version": "12.0.2.0.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "hr",
        "education",
    ],
    "data": [
        "data/hr_education_data.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_view.xml",
        "views/hr_employee_edu_type_view.xml",
        "views/hr_education_menu_view.xml",
        "reports/hr_employee_report_view.xml",
    ],
    "installable": True,
}
