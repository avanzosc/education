import json

from odoo import http, _
from odoo.http import request
from odoo.addons.education_evaluation_notebook.models.education_record import \
    RECORD_EXCEPTIONALITY
from odoo.addons.portal.controllers.portal import CustomerPortal

EVALUATIONS = {
    'first': _('FIRST'),
    'second': _('SECOND'),
    'third': _('THIRD'),
    'final': _('FINAL'),
}


class EducationMain(CustomerPortal):

    @http.route(['/meetings'], type='http',
                auth="user", website=True)
    def meetings(self, **args):
        logged_employee = request.env['hr.employee'].search([
            ('user_id', '=', request.uid)])

        calendar_event_obj = request.env['calendar.event']
        partner_obj = request.env['res.partner']

        if not logged_employee:
            return request.redirect('/main')

        current_academic_year = self.get_current_academic_year()

        meetings = calendar_event_obj.sudo().search([
            ('teacher_id', '=', logged_employee.id),
            ('academic_year_id', '=', current_academic_year.id),
        ], order='eval_type')

        change_ids = []
        eval_change_ids = {}
        for arg in args:
            vals = arg.split('_')
            if args[arg] != '':
                change_ids.append(int(vals[1]))
                eval_ids = eval_change_ids.get(vals[0], [])
                eval_ids.append(int(vals[1]))
                eval_change_ids.update({
                    vals[0]: eval_ids
                })

        meetings_change_students = partner_obj.sudo().search([
            ('id', 'in', change_ids)
        ])
        for eval in eval_change_ids:
            for student in meetings_change_students:
                student_meetigs = meetings.filtered(lambda m: m.student_id.id == student.id and m.eval_type == eval)
                new_value = int(args[eval+'_'+str(student.id)])
                if len(student_meetigs) > new_value:
                    self.update_meetings_done(student, new_value, eval, logged_employee, current_academic_year)

        evaluations = set(meetings.mapped('eval_type'))
        values = {
            'meetings': meetings,
            'students': meetings.mapped('student_id'),
            'evaluations': evaluations,
            'evaluations_str': EVALUATIONS,
        }

        return http.request.render(
            'education_evaluation_tutor_table.' +
            'student_meetings_table', values)

    def update_meetings_done(self, student, new_done, evaluation=None, teacher=None, academic_year=None):
        meetings = request.env['calendar.event'].sudo().search([
            ('teacher_id', '=', teacher.id),
            ('student_id', '=', student.id),
            ('academic_year_id', '=', academic_year.id),
            ('eval_type', '=', evaluation),
        ])
        meetings_to_update = new_done
        for meeting in meetings.filtered(lambda m: m.state not in ['done', 'cancel']):
            if meetings_to_update:
                meeting.action_open()
                meetings_to_update -= 1
