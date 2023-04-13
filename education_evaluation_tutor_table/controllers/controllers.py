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
MONTHS = {
    1: _('January'),
    2: _('February'),
    3: _('March'),
    4: _('April'),
    5: _('May'),
    6: _('June'),
    7: _('July'),
    8: _('August'),
    9: _('September'),
    10: _('October'),
    11: _('November'),
    12: _('December'),
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
            eval_ref = vals[0]
            student_id = int(vals[1])
            month_id = int(vals[2])
            type_ref = vals[3]
            if args[arg] != '':
                change_ids.append(student_id)
                eval_ids = eval_change_ids.get(eval_ref, [])
                if eval_ids != []:
                    eval_by_types = eval_ids.get(type_ref, {})
                    if month_id:
                        eval_ids = eval_by_types.get(month_id, [])
                eval_ids.append(int(vals[1]))
                eval_change_ids.update({
                    eval_ref: {
                        type_ref: {
                            month_id: eval_ids
                        }
                    }
                })

        meetings_change_students = partner_obj.sudo().search([
            ('id', 'in', change_ids)
        ])
        for eval in eval_change_ids:
            for type_ref in eval_change_ids[eval]:
                for month in eval_change_ids[eval][type_ref]:
                    for student in meetings_change_students:
                        student_meetigs = meetings.filtered(lambda m: m.student_id.id == student.id and m.eval_type == eval)
                        new_value = int(args[eval+'_'+str(student.id)+'_'+str(month)+'_'+type_ref])
                        if len(student_meetigs) > new_value:
                            self.update_meetings_done(
                                student, new_value, evaluation=eval, month=month,
                                type_ref=type_ref, teacher=logged_employee, academic_year=current_academic_year)

        evaluations = set(meetings.mapped('eval_type'))
        evaluation_months = {}
        for eval in evaluations:
            start_datetimes = meetings.filtered(lambda m: m.eval_type == eval).mapped('start_datetime')
            month_obj = {}
            for date in start_datetimes:
                meeting_ids = meetings.filtered(lambda m: m.eval_type == eval and m.start_datetime.month == date.month)
                month_obj.update({
                    date.month: meeting_ids.ids
                })
            evaluation_months.update({
                eval: month_obj
            })
        STUDENT_TUTORING, FAMILY_TUTORING = self.get_tutoring_types()
        values = {
            'meetings': meetings,
            'students': meetings.mapped('student_id'),
            'evaluations': evaluations,
            'evaluations_str': EVALUATIONS,
            'months_str': MONTHS,
            'evaluation_months': evaluation_months,
            'STUDENT_TUTORING': STUDENT_TUTORING.id,
            'FAMILY_TUTORING': FAMILY_TUTORING.id,
        }

        return http.request.render(
            'education_evaluation_tutor_table.' +
            'student_meetings_table', values)

    def update_meetings_done(self, student, new_done, evaluation=None, month=None, type_ref=None, teacher=None, academic_year=None):
        domain = [('student_id', '=', student.id)]
        STUDENT_TUTORING, FAMILY_TUTORING = self.get_tutoring_types()
        if academic_year:
            domain += [('academic_year_id', '=', academic_year.id)]
        if evaluation:
            domain += [('eval_type', '=', evaluation)]
        if teacher:
            domain += [('teacher_id', '=', teacher.id)]
        if type_ref == 'student':
            domain += [('categ_ids', 'in', STUDENT_TUTORING.ids)]
        elif type_ref == 'parent':
            domain += [('categ_ids', 'in', FAMILY_TUTORING.ids)]

        meetings = request.env['calendar.event'].sudo().search(domain)
        if month:
            meetings = meetings.filtered(lambda m: m.start_datetime.month == month)
        meetings_to_update = new_done
        for meeting in meetings.filtered(lambda m: m.state not in ['done', 'cancel']):
            if meetings_to_update:
                meeting.action_open()
                meetings_to_update -= 1

    def get_tutoring_types(self):
        STUDENT_TUTORING = request.env.ref(
            "calendar_school.calendar_event_type_student_tutoring",
            raise_if_not_found=False)
        FAMILY_TUTORING = request.env.ref(
            "calendar_school.calendar_event_type_family_tutoring",
            raise_if_not_found=False)
        return STUDENT_TUTORING, FAMILY_TUTORING
