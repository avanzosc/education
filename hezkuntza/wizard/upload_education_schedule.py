# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info,\
    _convert_time_str_to_float
from odoo import _, exceptions, fields, models
from odoo.addons.resource_education.models.resource_calendar import\
    EDUCATION_DAYOFWEEK_CODE


class UploadEducationContractType(models.TransientModel):
    _name = 'upload.education.schedule'
    _description = 'Wizard to Upload Schedule'

    file = fields.Binary(
        string='Schedule File', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        schedule_obj = self.env[
            'education.schedule'].with_context(active_test=False)
        timetable_obj = self.env[
            'education.schedule.timetable'].with_context(active_test=False)
        partner_obj = self.env['res.partner'].with_context(active_test=False)
        academic_year_obj = self.env[
            'education.academic_year'].with_context(active_test=False)
        idtype_obj = self.env[
            'education.idtype'].with_context(active_test=False)
        employee_obj = self.env['hr.employee'].with_context(active_test=False)
        task_type_obj = self.env[
            'education.task_type'].with_context(active_test=False)
        classroom_obj = self.env[
            'education.classroom'].with_context(active_test=False)
        subject_obj = self.env[
            'education.subject'].with_context(active_test=False)
        language_obj = self.env[
            'education.language'].with_context(active_test=False)
        group_obj = self.env[
            'education.schedule.group'].with_context(active_test=False)
        edu_group_obj = self.env['education.group'].with_context(
            active_test=False)
        dayofweek_dict = dict(map(reversed, EDUCATION_DAYOFWEEK_CODE.items()))
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    line_type = _format_info(line[:1])
                    if line_type == '1':
                        center_code = _format_info(line[3:9])
                        center = partner_obj.search([
                            ('education_code', '=', center_code),
                            ('educational_category', '=', 'school'),
                        ], limit=1)
                        year = _format_info(line[9:13])
                        academic_year = academic_year_obj.search([
                            ('name', 'ilike', '{}-'.format(year)),
                        ], limit=1)
                    if line_type == '2':
                        if not center or not academic_year:
                            break
                        doc_type = _format_info(line[1:5])
                        idtype = idtype_obj.search([
                            ('education_code', '=', doc_type),
                        ], limit=1)
                        doc = _format_info(line[5:20])
                        teacher = employee_obj.search([
                            ('edu_idtype_id', '=', idtype.id),
                            ('identification_id', '=', doc),
                        ], limit=1)
                        if not teacher:
                            continue
                        session_number = int(_format_info(line[20:22]))
                        dayofweek = dayofweek_dict.get(
                            int(_format_info(line[22:23])))
                        task_type = task_type_obj.search([
                            ('education_code', '=', _format_info(line[23:27])),
                        ])
                        hour_from = _convert_time_str_to_float(
                            _format_info(line[27:32]))
                        hour_to = _convert_time_str_to_float(
                            _format_info(line[32:37]))
                        classroom = classroom_obj.search([
                            ('center_id', '=', center.id),
                            ('education_code', '=', _format_info(line[37:45]))
                        ])
                        if not classroom:
                            continue
                        schedule = schedule_obj.search([
                            ('center_id', '=', center.id),
                            ('academic_year_id', '=', academic_year.id),
                            # ('session_number', '=', session_number),
                            # ('dayofweek', '=', dayofweek),
                            ('teacher_id', '=', teacher.id),
                            ('classroom_id', '=', classroom.id),
                        ])
                        vals = {
                            'center_id': center.id,
                            'academic_year_id': academic_year.id,
                            # 'session_number': session_number,
                            # 'dayofweek': dayofweek,
                            'teacher_id': teacher.id,
                            # 'hour_from': hour_from,
                            # 'hour_to': hour_to,
                            'task_type_id': task_type.id,
                            'classroom_id': classroom.id,
                        }
                        timetable_vals = {
                            'session_number': session_number,
                            'dayofweek': dayofweek,
                            'hour_from': hour_from,
                            'hour_to': hour_to,
                        }
                        if task_type.type == 'L':
                            subject_code = _format_info(line[45:53])
                            subject = subject_obj.search([
                                ('education_code', '=', subject_code),
                            ])
                            if not subject and not subject_code == '00000000':
                                continue
                            subject_type = _format_info(line[53:54])
                            language = language_obj.search([
                                ('education_code', '=',
                                 _format_info(line[54:56])),
                            ])
                            vals.update({
                                'subject_id': subject.id,
                                'subject_type': subject_type,
                                'language_id': language.id,
                            })
                            if schedule:
                                schedule = schedule.filtered(
                                    lambda s: s.subject_id == subject and
                                    s.subject_type == subject_type and
                                    s.language_id == language)
                        # elif task_type.type == 'N':
                        #     activity_type = _format_info(line[45:48])
                        #     level = _format_info(line[48:52])
                        #     plan = _format_info(line[52:56])
                        if schedule:
                            timetable = timetable_obj.search(
                                [('schedule_id', '=', schedule.id),
                                 ('dayofweek', '=', dayofweek),
                                 ('hour_from', '=', hour_from),
                                 ('hour_to', '=', hour_to)])
                            if not timetable:
                                vals.update({
                                    'timetable_ids': [(0, 0, timetable_vals)]
                                })
                            schedule.write(vals)
                        else:
                            vals.update({
                                'timetable_ids': [(0, 0, timetable_vals)]
                            })
                            schedule = schedule_obj.create(vals)
                    if line_type == '3':
                        try:
                            group_code = _format_info(line[1:9])
                            imp_group = edu_group_obj.search([
                                ('education_code', '=', group_code),
                                ('center_id', '=', center.id),
                                ('academic_year_id', '=', academic_year.id),
                            ])
                            if schedule and imp_group:
                                schedule.write({
                                    'group_ids': [(4, imp_group.id)],
                                })
                            group_code2 = _format_info(line[67:76])
                            off_group = edu_group_obj.search([
                                ('education_code', '=', group_code2),
                                ('center_id', '=', center.id),
                                ('academic_year_id', '=', academic_year.id),
                            ])
                            session_number = int(_format_info(line[9:13]))
                            student_count = int(_format_info(line[13:17]))
                            alias = _format_info(line[17:67])
                            if imp_group and off_group:
                                vals = {
                                    'schedule_id': schedule.id,
                                    'group_id': imp_group.id,
                                    'session_number': session_number,
                                    'student_count': student_count,
                                    'group_alias': alias,
                                    'parent_group_id': off_group.id,
                                }
                                group = group_obj.search([
                                    ('schedule_id', '=', schedule.id),
                                    ('group_id', '=', imp_group.id),
                                ])
                                if group:
                                    group.write(vals)
                                # else:
                                #     group_obj.create(vals)
                        except Exception:
                            pass
        action = self.env.ref('education.action_education_schedule')
        return action.read()[0]
