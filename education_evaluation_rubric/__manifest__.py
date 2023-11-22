# Copyright 2022 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Education Evaluation Rubric",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/education",
    "depends": [
        "education",
        "education_evaluation_notebook",
        "survey_usability",
    ],
    "data": [
        "security/education_survey.xml",
        "security/ir.model.access.csv",
        "data/education_competence_data.xml",
        "views/templates.xml",
        "views/education_exam_views.xml",
        "views/education_notebook_line_views.xml",
        "views/education_record_views.xml",
        "views/education_schedule_views.xml",
        "views/survey_question_views.xml",
        "views/survey_survey_views.xml",
        "views/survey_user_input_views.xml",
        "views/report_partner_record_template.xml",
        # "views/views.xml",
    ],
    "installable": True,
}
