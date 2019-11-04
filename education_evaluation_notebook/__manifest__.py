# Copyright (c) 2019 Adrian Revilla <adrianrevilla@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
      'views/education_notebook_stuff_view.xml',
      'views/education_notebook_competence_view.xml',
      'views/education_notebook_exam_view.xml',
      'views/education_schedule_view.xml',
      'views/education_notebook_line_view.xml',
      'views/education_notebook_expedient_view.xml',
      'views/education_notebook_menu_view.xml',
    ],
    'installable': True,
}
