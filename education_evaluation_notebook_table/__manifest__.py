# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Education Evaluation Notebook - Teacher Table",
    "summary": "Show teacher table on website from portal"
               " or from education schedule",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "portal",
        "website",
        "education_evaluation_notebook",
    ],
    "data": [
        "views/templates.xml",
        "views/views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
