# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Contacts for Education Centers",
    "version": "12.0.7.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "education",
        "contacts_school",
        "contacts_school_permission",
        "partner_contact_gender",
        "partner_language_skill",
        "res_partner_student_fields",
    ],
    "data": [
        "data/education_task_type_data.xml",
        "security/ir.model.access.csv",
        "security/contacts_school_education_rules.xml",
        "reports/education_group_student_progenitor_report_view.xml",
        "views/education_course_change_view.xml",
        "views/res_partner_lang_skill_view.xml",
        "views/res_partner_permission_view.xml",
        "views/res_partner_view.xml",
        "wizards/education_group_next_year_schedule_view.xml",
        "reports/partner_insurance_xlsx_report.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
