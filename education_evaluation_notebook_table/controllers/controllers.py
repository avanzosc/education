
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EducationMain(CustomerPortal):

    @http.route(['/schedules'], type='http',
                auth="user", website=True)
    def schedule(self):

        logged_employee = request.env['hr.employee'].search([
            ('user_id', '=', request.uid)])

        if not logged_employee:
            return request.redirect('/main')

        schedule_obj = request.env['education.schedule']
        current_academic_year = self.get_current_academic_year()

        schedules = schedule_obj.sudo().search([
            ('academic_year_id', '=', current_academic_year.id),
            ('teacher_id', '=', logged_employee.id)
        ])

        values = {
            'schedules': schedules,
        }

        return http.request.render(
            'education_evaluation_notebook_table.' +
            'teacher_schedule_table', values)

    @http.route(['/schedule/<int:schedule_id>/califications'], type='http',
                auth="user", website=True)
    def schedule_califications(self, schedule_id=None):

        logged_employee = request.env['hr.employee'].search([
            ('user_id', '=', request.uid)])

        if not logged_employee:
            return request.redirect('/main')

        schedule_obj = request.env['education.schedule']

        schedule = schedule_obj.sudo().browse(schedule_id)
        schedule_evaluation_records = schedule.record_ids
        evaluation_record_students = schedule_evaluation_records.mapped('student_id')

        record_lines = schedule_evaluation_records.mapped('n_line_id')

        values = {
            'schedule': schedule,
            'schedule_evaluation_records': schedule_evaluation_records,
            'evaluation_record_students': evaluation_record_students,
            'record_lines': record_lines,
        }

        return http.request.render(
            'education_evaluation_notebook_table.' +
            'schedule_calification_table', values)
