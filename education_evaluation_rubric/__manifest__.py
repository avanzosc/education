# Copyright 2022 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Education Evaluation Rubric",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "education_evaluation_notebook",
        "survey_usability",
    ],
    "data": [
        "data/education_competence_data.xml",
        "views/templates.xml",
        "views/views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
