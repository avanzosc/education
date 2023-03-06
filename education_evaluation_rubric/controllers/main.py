
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.survey.controllers.main import Survey


class WebsiteSurvey(Survey):

    @http.route()
    def print_survey(self, survey, token, **post):
        res = super().print_survey(survey, token, **post)
        survey_input = request.env['survey.user_input'].sudo().search([
            ('token', '=', token)
        ], limit=1)
        if survey_input:
            schedule = survey_input.education_record_id.schedule_id
            if survey_input.exam_id:
                input_ids = survey.user_input_ids.filtered(
                    lambda i: i.exam_id == survey_input.exam_id)
            else:
                input_ids = survey.user_input_ids.filtered(
                    lambda i: i.notebook_line_id.id == survey_input.notebook_line_id.id and not i.exam_id)
            is_next = False
            next_student_input = None
            for index, item in enumerate(input_ids):
                if is_next:
                    next_student_input = item
                    break
                if survey_input == item:
                    is_next = True
            if next_student_input:
                trail = "/%s" % next_student_input.token if next_student_input else ""
                link_next_student = survey.with_context(relative_url=True).public_url + trail
                res.qcontext.update({
                    'link_next_student': link_next_student})
            res.qcontext.update({
                'student_ids': schedule.student_ids,
                'survey_input': survey_input,
                'schedule': schedule,
                'input_ids': input_ids,
            })
        return res
        
    @http.route()
    def fill_survey(self, survey, token, prev=None, **post):
        res = super().fill_survey(survey, token, prev, **post)
        survey_input = request.env['survey.user_input'].sudo().search([
            ('token', '=', token)
        ], limit=1)
        if survey_input:
            if survey_input.state == 'done':
                return request.redirect('/survey/print/%s/%s' % (survey.id, survey_input.token))
            schedule = survey_input.education_record_id.schedule_id
            if survey_input.exam_id:
                input_ids = survey.user_input_ids.filtered(
                    lambda i: i.exam_id == survey_input.exam_id)
            else:
                input_ids = survey.user_input_ids.filtered(
                    lambda i: i.notebook_line_id.id == survey_input.notebook_line_id.id and not i.exam_id)
            is_next = False
            next_student_input = None
            for index, item in enumerate(input_ids):
                if is_next:
                    next_student_input = item
                    break
                if survey_input == item:
                    is_next = True
            if next_student_input:
                trail = "/%s" % next_student_input.token if next_student_input else ""
                link_next_student = survey.with_context(relative_url=True).public_url + trail
                res.qcontext.update({
                    'link_next_student': link_next_student})
            res.qcontext.update({
                'student_ids': schedule.student_ids,
                'survey_input': survey_input,
                'input_ids': input_ids,
            })
        return res
        
    @http.route()
    def start_survey(self, survey, token=None, **post):
        res = super().start_survey(survey, token, **post)
        survey_input = request.env['survey.user_input'].sudo().search([
            ('token', '=', token)
        ], limit=1)
        if survey_input:
            schedule = survey_input.education_record_id.schedule_id
            if survey_input.exam_id:
                input_ids = survey.user_input_ids.filtered(
                    lambda i: i.exam_id == survey_input.exam_id)
            else:
                input_ids = survey.user_input_ids.filtered(
                    lambda i: i.notebook_line_id.id == survey_input.notebook_line_id.id and not i.exam_id)
            res.qcontext.update({
                'student_ids': schedule.student_ids,
                'survey_input': survey_input,
                'input_ids': input_ids,
            })
        return res
