# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Education Evaluation Notebook",
    "version": "12.0.1.0.0",
    "depends": [
        "education",
        "contacts_school",
        "contacts_school_education",
        "mail",
        "portal",
    ],
    "author":  "AvanzoSC",
    "license": "AGPL-3",
    "website": "http://www.avanzosc.es",
    "data": [
        "security/ir.model.access.csv",
        "data/education_evaluation_notebook_data.xml",
        "views/education_academic_year_evaluation_view.xml",
        "views/education_competence_type_view.xml",
        "views/education_competence_view.xml",
        "views/education_exam_type_view.xml",
        "views/education_exam_view.xml",
        "views/education_homework_view.xml",
        "views/education_mark_behaviour_view.xml",
        "views/education_mark_numeric_view.xml",
        "views/education_schedule_view.xml",
        "views/education_notebook_line_view.xml",
        "views/education_record_view.xml",
        "views/education_notebook_menu_view.xml",
        "views/res_partner_view.xml",
        "wizards/create_academic_year_evaluation_view.xml",
    ],
    "installable": True,
}
