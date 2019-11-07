# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Education Evaluation Notebook',
    'version': '12.0.1.0.0',
    'depends': [
        'education',
    ],
    'author':  "AvanzoSC",
    'license': "AGPL-3",
    'summary': '''Education Evaluation Notebook''',
    'website': 'http://www.avanzosc.es',
    'data': [
      'security/ir.model.access.csv',
      'wizard/education_notebook_exam_check.xml',
      'views/education_notebook_stuff_view.xml',
      'views/education_academic_year_evaluation_view.xml',
      'views/education_notebook_homework_view.xml',
      'views/education_notebook_competence_view.xml',
      'views/education_notebook_exam_view.xml',
      'views/education_schedule_view.xml',
      'views/education_notebook_line_view.xml',
      'views/education_notebook_record_view.xml',
      'views/education_notebook_menu_view.xml',
    ],
    'installable': True,
}
