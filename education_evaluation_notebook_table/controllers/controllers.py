import json

from odoo import http, _
from odoo.http import request
from odoo.addons.education_evaluation_notebook.models.education_record import \
    RECORD_EXCEPTIONALITY
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.addons.website.controllers.main import QueryURL


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

    @http.route(['/schedule/action'], type='json',
                auth="user", methods=['POST'], website=True, csrf=False)
    def schedule_califications_json(self, schedule_id, vals, n_line, **kw):

        error = False
        action = False
        domain = [
            ('schedule_id', '=', int(schedule_id)),
        ]
        if 'exam' in vals:
            domain += [('exam_id', '=', int(n_line))]
            exam = request.env['education.exam'].sudo().browse(int(n_line))
        else:
            domain += [('n_line_id', '=', int(n_line))]
            exam = None
        records = request.env['education.record'].sudo().search(domain)
        if records:
            if 'copy' in vals:
                action = vals.get('copy')
                records.action_copy_partial_calculated_mark()
            if 'initial' in vals:
                action = vals.get('initial')
                if exam:
                    exam.action_marking()
                else:
                    records.button_set_draft()
            if 'assessed' in vals:
                action = vals.get('assessed')
                if exam:
                    exam.action_graded()
                else:
                    records.button_set_assessed()
            if 'round' in vals:
                action = vals.get('round')
                records.action_round_numeric_mark()

        return {str(action): not error}

    @http.route(['/schedule/<int:schedule_id>/califications'], type='http',
                auth="user", website=True)
    def schedule_califications(
            self, schedule_id=None, changed_input_ids=None,
            changed_select_ids=None, download=False, report_type=None,
            access_token=None, **args):

        logged_employee = request.env['hr.employee'].search([
            ('user_id', '=', request.uid)])

        if not logged_employee:
            return request.redirect('/main')

        if report_type:
            self.print_schedule_record_reports(
                schedule_id, report_type, download, access_token)

        if changed_input_ids:
            changed_input_ids_array = json.loads(changed_input_ids)
            self.update_new_schedule_records(
                changed_input_ids_array, 'numeric_mark')
        if changed_select_ids:
            changed_select_ids_array = json.loads(changed_select_ids)
            self.update_new_schedule_records(
                changed_select_ids_array, 'exceptionality')

        schedule_obj = request.env['education.schedule']

        schedule = schedule_obj.sudo().browse(schedule_id)
        schedule_evaluation_records = schedule.record_ids
        evaluation_record_students = schedule_evaluation_records.mapped(
            'student_id')

        record_lines = schedule_evaluation_records.mapped('n_line_id')
        evaluations = record_lines.filtered(
            lambda l: l.competence_id.evaluation_check or l.competence_id.global_check)
        retake_record_lines = self.get_retake_record_lines(record_lines)

        url = '/schedule/%s/califications' % schedule_id
        keep = QueryURL(url, access_token=access_token)
        values = {
            'keep': keep,
            'schedule': schedule,
            'schedule_evaluation_records': schedule_evaluation_records,
            'evaluation_record_students': evaluation_record_students,
            'record_lines': record_lines,
            'retake_record_lines': retake_record_lines,
            'evaluations': evaluations,
            'exceptionalities': self.get_record_exceptionality_library(),
        }

        return http.request.render(
            'education_evaluation_notebook_table.' +
            'schedule_calification_table', values)

    def get_retake_record_lines(self, record_lines):
        retake_record_lines = None
        for line in record_lines:
            line_records = line.record_ids.filtered(lambda r: r.is_retake_record)
            if line_records:
                retake_record_lines = retake_record_lines + line if retake_record_lines else line
        print('!!', retake_record_lines)
        return retake_record_lines

    def get_record_exceptionality_library(self):
        exceptionality_lib = {}
        for exceptionality in RECORD_EXCEPTIONALITY:
            exceptionality_lib.update({
                exceptionality[0]: _(exceptionality[1])
            })
        return exceptionality_lib

    def update_new_schedule_records(self, new_values_array, field_type):
        record_obj = request.env['education.record']
        for value in new_values_array:
            record_id = value['record_id']
            new_val = value['new_val']
            edu_record = record_obj.sudo().browse(int(record_id))
            if edu_record and (new_val or field_type == 'exceptionality'):
                update_ok = None
                if field_type == 'numeric_mark':
                    if self.check_value_spelling(new_val):
                        new_val = float(new_val.replace(' ', '').replace(',', '.'))
                        if (edu_record.competence_id.min_mark <= new_val <=
                                edu_record.competence_id.max_mark):
                            update_ok = True
                    else:
                        update_ok = False
                if field_type == 'exceptionality':
                    if new_val == "":
                        new_val = None
                    update_ok = True
                if update_ok:
                    edu_record.sudo().update({field_type: new_val})
        return True

    def check_value_spelling(self, new_val):
        comma_dot_count = len(
            [pos for pos, char in enumerate(new_val) if char in [',', '.']])
        if comma_dot_count > 1:
            return False
        return True

    def print_schedule_record_reports(
            self, schedule_id, report_type, download, access_token):
        try:
            partner_sudo = self._document_check_access(
                'education.schedule', schedule_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/schedules')
        if report_type in ('html', 'pdf', 'text'):
            report_ref = (
                'education_evaluation_notebook_table'
                '.schedule_academic_record_report_xlsx')
            return self._show_report(
                model=partner_sudo, report_type=report_type,
                report_ref=report_ref,
                download=download)
