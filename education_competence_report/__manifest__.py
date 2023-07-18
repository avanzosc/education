# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Education Competence Report",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "education",
        "education_evaluation_notebook",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "reports/education_group_competence_report_view.xml",
        "reports/education_schedule_criteria_report_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
