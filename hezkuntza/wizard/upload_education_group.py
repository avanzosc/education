# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationGroup(models.TransientModel):
    _name = 'upload.education.group'
    _description = 'Wizard to Upload Groups'

    file = fields.Binary(
        string='Groups', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        partner_obj = self.env['res.partner']
        academic_year_obj = self.env[
            'education.academic_year'].with_context(active_test=False)
        group_obj = self.env['education.group'].with_context(active_test=False)
        plan_obj = self.env['education.plan'].with_context(active_test=False)
        level_obj = self.env['education.level'].with_context(active_test=False)
        field_obj = self.env['education.field'].with_context(active_test=False)
        shift_obj = self.env['education.shift'].with_context(active_test=False)
        course_obj = self.env['education.course'].with_context(
            active_test=False)
        model_obj = self.env['education.model'].with_context(active_test=False)
        group_type_obj = self.env[
            'education.group_type'].with_context(active_test=False)
        calendar_obj = self.env['resource.calendar']
        classroom_obj = self.env[
            'education.classroom'].with_context(active_test=False)
        idtype_obj = self.env[
            'education.idtype'].with_context(active_test=False)
        group_teacher_obj = self.env[
            'education.group.teacher'].with_context(active_test=False)
        employee_obj = self.env['hr.employee'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    line_type = _format_info(line[:1])
                    if line_type == '1':
                        center_code = _format_info(line[3:9])
                        partner = partner_obj.search([
                            ('education_code', '=', center_code),
                            ('educational_category', '=', 'school'),
                        ])
                        year = _format_info(line[9:13])
                        academic_year = academic_year_obj.search([
                            ('name', 'ilike', '{}-'.format(year)),
                        ])
                    if line_type == '2' and partner:
                        group_code = _format_info(line[1:9])
                        plan = plan_obj.search([
                            ('education_code', '=', _format_info(line[59:63])),
                        ])
                        level = level_obj.search([
                            ('education_code', '=', _format_info(line[63:67])),
                            ('plan_id', '=', plan.id)])
                        field = field_obj.search([
                            ('education_code', '=', _format_info(line[67:71])),
                        ])
                        shift = shift_obj.search([
                            ('education_code', '=', _format_info(line[71:75])),
                        ], limit=1)
                        course = course_obj.search([
                            ('education_code', '=', _format_info(line[75:79])),
                            ('plan_id', '=', plan.id),
                            ('level_id', '=', level.id),
                            ('field_id', '=', field.id),
                            ('shift_id', '=', shift.id),
                        ], limit=1)
                        classroom = classroom_obj.search([
                            ('education_code', '=',
                             _format_info(line[539:547])),
                            ('center_id', '=', partner.id),
                        ], limit=1)
                        model = model_obj.search([
                            ('education_code', '=', _format_info(line[79:83])),
                        ], limit=1)
                        group_type = group_type_obj.search([
                            ('education_code', '=', _format_info(line[83:87])),
                        ], limit=1)
                        calendar = calendar_obj.search([
                            ('education_code', '=', _format_info(line[87:95])),
                            ('center_id', '=', partner.id),
                        ])
                        vals = {
                            'center_id': partner.id,
                            'academic_year_id': academic_year.id,
                            'education_code': group_code,
                            'description': _format_info(line[9:59]),
                            'plan_id': plan.id,
                            'level_id': level.id,
                            'field_id': field.id,
                            'shift_id': shift.id,
                            'course_id': course.id,
                            'model_id': model.id,
                            'group_type_id': group_type.id,
                            'calendar_id': calendar.id,
                            'comments': _format_info(line[289:539]),
                            'classroom_id': classroom.id,
                        }
                        groups = group_obj.search([
                            ('education_code', '=', group_code),
                            ('center_id', '=', partner.id)])
                        if groups:
                            groups.write(vals)
                        else:
                            groups = group_obj.create(vals)
                        start = 95
                        for i in range(1, 11):
                            end = start + 4
                            doc_type = _format_info(line[start:end])
                            idtype = idtype_obj.search([
                                ('education_code', '=', doc_type),
                            ], limit=1)
                            start = end + 15
                            doc = _format_info(line[end:start])
                            teacher = employee_obj.search([
                                ('edu_idtype_id', '=', idtype.id),
                                ('identification_id', '=', doc),
                            ], limit=1)
                            teacher_vals = {
                                'group_id': groups.id,
                                'sequence': i,
                                'employee_id': teacher.id,
                            }
                            teachers = group_teacher_obj.search([
                                ('group_id', '=', groups.id),
                                ('sequence', '=', i)])
                            if teachers:
                                teachers.write(teacher_vals)
                            else:
                                group_teacher_obj.create(teacher_vals)
                            if doc:
                                print('document: [{}] {}'.format(
                                    doc_type, doc))
                        # student_count = _format_info(line[285:289])
                    # if line_type == '3':
                    #     group_code = _format_info(line[1:9])
                    #     session = _format_info(line[9:11])
                    #     weekday = _format_info(line[11:12])
                    #     start = _format_info(line[12:17])
                    #     end = _format_info(line[17:22])
                    #     recess = _format_info(line[22:23])
        action = self.env.ref('education.action_education_group')
        return action.read()[0]
