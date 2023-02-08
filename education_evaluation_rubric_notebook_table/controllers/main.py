
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EducationMain(CustomerPortal):

    def schedule_califications_json(self, schedule_id, action, n_line, is_exam=None):
        super().schedule_califications_json(schedule_id, action, n_line, is_exam)
        #
        # n_line = request.env['education.notebook.line'].browse(int(n_line))
        # if n_line:
        #     if action == 'rubric':
        #         res = n_line.button_open_all_survey_inputs()
        #         url = res.get('url', None)
        #         if url:
        #             request.redirect(url)
