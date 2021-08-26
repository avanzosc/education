import json

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
    def schedule_califications(
            self, schedule_id=None, changed_input_ids=None, **args):

        logged_employee = request.env['hr.employee'].search([
            ('user_id', '=', request.uid)])

        if not logged_employee:
            return request.redirect('/main')

        if changed_input_ids:
            changed_input_ids_array = json.loads(changed_input_ids)
            self.update_new_schedule_records(changed_input_ids_array)

        schedule_obj = request.env['education.schedule']

        schedule = schedule_obj.sudo().browse(schedule_id)
        schedule_evaluation_records = schedule.record_ids
        evaluation_record_students = schedule_evaluation_records.mapped(
            'student_id')

        record_lines = schedule_evaluation_records.mapped('n_line_id')
        evaluations = record_lines.filtered(
            lambda l: l.competence_id.evaluation_check or l.competence_id.global_check)

        values = {
            'schedule': schedule,
            'schedule_evaluation_records': schedule_evaluation_records,
            'evaluation_record_students': evaluation_record_students,
            'record_lines': record_lines,
            'evaluations': evaluations,
        }

        return http.request.render(
            'education_evaluation_notebook_table.' +
            'schedule_calification_table', values)

    def update_new_schedule_records(self, new_values_array):
        record_obj = request.env['education.record']
        for value in new_values_array:
            record_id = value['record_id']
            new_val = value['new_val']
            edu_record = record_obj.sudo().browse(int(record_id))
            if edu_record and new_val:
                new_val = float(new_val)
                if edu_record.competence_id.min_mark <= new_val <= edu_record.competence_id.max_mark:
                    edu_record.sudo().update({'numeric_mark': new_val})
        return True
