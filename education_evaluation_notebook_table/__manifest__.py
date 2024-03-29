# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Education Evaluation Notebook - Teacher Table",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/education",
    "depends": [
        "portal",
        "website",
        "education_evaluation_notebook",
    ],
    "data": [
        "reports/academic_record_report_view.xml",
        "wizards/print_education_schedule_records_view.xml",
        "views/templates.xml",
        "views/views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
