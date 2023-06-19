# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Education Evaluation Notebook - Tutor Table",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "portal",
        "website",
        "report_xlsx",
        "education",
        "calendar_school",
        "education_evaluation_notebook",
    ],
    "data": [
        "views/views.xml",
        "views/templates.xml",
    ],
    "installable": True,
    "auto_install": True,
}
