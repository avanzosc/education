# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Education Notebook Observation",
    "version": "12.0.1.2.0",
    "depends": [
        "calendar_school",
        "contacts_school",
        "education_evaluation_notebook",
        "education_center_mail_template"
    ],
    "author":  "AvanzoSC",
    "license": "AGPL-3",
    "website": "http://www.avanzosc.es",
    "data": [
        "security/ir.model.access.csv",
        "security/education_notebook_observation_rules.xml",
        "data/education_notebook_observation.xml",
        "wizard/wiz_generate_notebook_observation_view.xml",
        "wizard/wiz_send_notebook_observation_email_view.xml",
        "views/education_notebook_observation_view.xml",
        "views/res_partner_view.xml",
        "views/calendar_event_view.xml",
        "views/hr_employee_view.xml",
    ],
    "installable": True,
}
