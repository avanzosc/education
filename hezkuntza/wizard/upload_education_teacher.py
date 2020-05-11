# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info,\
    _convert_time_str_to_float
from odoo import _, exceptions, fields, models
from datetime import datetime


class UploadEducationTeacher(models.TransientModel):
    _name = 'upload.education.teacher'
    _description = 'Wizard to Upload Teachers'

    file = fields.Binary(
        string='Teachers (T06)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        teaching_staff = self.env.ref("hr_education.teaching_edu_type")
        company_obj = self.env["res.company"].sudo().with_context(
            active_test=False)
        partner_obj = self.env['res.partner'].with_context(active_test=False)
        employee_obj = self.env['hr.employee'].with_context(active_test=False)
        hr_contract_obj = self.env['hr.contract'].with_context(
            active_test=False)
        department_obj = self.env['hr.department'].with_context(
            active_test=False)
        user_obj = self.env['res.users'].with_context(active_test=False)
        academic_year_obj = self.env[
            'education.academic_year'].with_context(active_test=False)
        idtype_obj = self.env[
            'education.idtype'].with_context(active_test=False)
        position_obj = self.env[
            'education.position'].with_context(active_test=False)
        designation_obj = self.env[
            'education.designation_level'].with_context(active_test=False)
        workday_type_obj = self.env[
            'education.workday_type'].with_context(active_test=False)
        contract_type_obj = self.env[
            'education.contract_type'].with_context(active_test=False)
        workreason_obj = self.env['education.work_reason'].with_context(
            active_test=False)
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
                        ])
                        year = _format_info(line[9:13])
                        academic_year = academic_year_obj.search([
                            ('name', 'ilike', '{}-'.format(year)),
                        ])
                        company = company_obj.search([
                            ('partner_id', '=',
                             center.parent_id.id or center.id),
                        ], limit=1)
                        if not company:
                            company = company_obj.search([
                                ('parent_id', '=', False),
                            ], limit=1)
                    if line_type == '2':
                        op_type = _format_info(line[1:2])
                        id_type = idtype_obj.search([
                            ('education_code', '=', _format_info(line[2:6]))])
                        id_number = _format_info(line[6:21])
                        employee = employee_obj.search([
                            ('edu_idtype_id', '=', id_type.id),
                            ('identification_id', '=', id_number),
                        ])
                        partner = partner_obj.search([
                            ('edu_idtype_id', '=', id_type.id),
                            ('vat', 'ilike', id_number),
                        ])
                        if len(partner) > 1:
                            continue
                        user = employee.user_id
                        if not user and id_number:
                            user = user_obj.search([
                                    ('vat', 'ilike', id_number),
                                    ('edu_idtype_id', '=', id_type.id)])
                        if len(user) > 1:
                            continue
                        contract = hr_contract_obj.search([
                            ('employee_id', '=', employee.id),
                            ('ed_center_id', '=', center.id),
                            ('ed_academic_year_id', '=', academic_year.id),
                            ('state', 'not in', ['close', 'cancel'])
                        ])
                        if op_type == 'M':
                            # MODIFICACIÓN o ALTA
                            lastname = _format_info(line[21:71])
                            lastname2 = _format_info(line[71:121])
                            firstname = _format_info(line[121:151])
                            fullname = partner_obj._get_computed_name(
                                lastname, firstname, lastname2)
                            position1 = position_obj.search([
                                ('type', '=', 'normal'),
                                ('education_code', '=',
                                 _format_info(line[151:154])),
                            ])
                            position2 = position_obj.search([
                                ('type', '=', 'normal'),
                                ('education_code', '=',
                                 _format_info(line[154:157])),
                            ])
                            position3 = position_obj.search([
                                ('type', '=', 'other'),
                                ('education_code', '=',
                                 _format_info(line[157:160])),
                            ])
                            department_name = _format_info(line[160:310])
                            department = department_obj.search([
                                ('name', '=', department_name)
                            ])
                            if not department:
                                department_obj.create({
                                    'name': department_name,
                                })
                            dcode = '0{}'.format(_format_info(line[310:312]))
                            designation = designation_obj.search([
                                ('education_code', '=', dcode),
                            ])
                            wcode = '00000{}'.format(
                                    _format_info(line[312:316]))
                            workday_type = workday_type_obj.search([
                                ('education_code', '=', wcode),
                            ])
                            work_hours = _convert_time_str_to_float(
                                _format_info(line[316:321]))
                            class_hours = _convert_time_str_to_float(
                                _format_info(line[321:326]))
                            age = _format_info(line[326:327]) == '1'
                            health = _format_info(line[327:328]) == '1'
                            notes = _format_info(line[328:578])
                            workreason = workreason_obj.search([
                                ('education_code', '=',
                                 _format_info(line[578:582]))
                            ])
                            date_str = _format_info(line[582:590])
                            if date_str != '':
                                date_start = datetime.strptime(
                                    date_str, '%d%m%Y')
                            else:
                                date_start = fields.Datetime.now()
                            date_start = fields.Datetime.to_string(date_start)
                            contract_type = contract_type_obj.search([
                                ('education_code', '=',
                                 _format_info(line[590:594])),
                            ])
                            contract_hours = _convert_time_str_to_float(
                                _format_info(line[594:599]))
                            vals = {
                                'name': fullname,
                                'edu_type_id': teaching_staff.id,
                                'company_id': False,
                            }
                            if not user:
                                user_vals = {
                                    'login': partner.email or id_number,
                                    'vat': 'ES{}'.format(id_number),
                                    'edu_idtype_id': id_type.id,
                                    'lastname': lastname,
                                    'lastname2': lastname2,
                                    'firstname': firstname,
                                    'partner_id': partner.id,
                                    'school_ids': [(4, center.id)],
                                    'company_ids': [(4, center.company_id.id)],
                                }
                                user_vals.update(vals)
                                user_vals["company_id"] = center.company_id.id
                                user = user_obj.with_context(
                                    no_reset_password=True).create(user_vals)
                            else:
                                user.write({
                                    'school_ids': [(4, center.id)],
                                    'company_ids': [(4, center.company_id.id)],
                                })
                            if not employee:
                                employee_vals = {
                                    'edu_idtype_id': id_type.id,
                                    'identification_id': id_number,
                                    'user_id': user.id,
                                    'gender': False,
                                    'marital': False,
                                    'address_home_id': user.partner_id.id,
                                    'department_id': department.id,
                                }
                                employee_vals.update(vals)
                                employee = employee_obj.create(employee_vals)
                            else:
                                if not employee.user_id:
                                    vals.update({
                                        'user_id': user.id,
                                        'address_home_id': user.partner_id.id,
                                    })
                                employee.write(vals)
                            contract_vals = {
                                'name': '[{}] {}'.format(
                                    academic_year.display_name,
                                    employee.display_name),
                                'employee_id': employee.id,
                                'department_id': department.id,
                                'ed_center_id': center.id,
                                'ed_academic_year_id': academic_year.id,
                                'date_start': date_start,
                                'ed_position_id': position1.id,
                                'ed_position2_id': position2.id,
                                'ed_otherposition_id': position3.id,
                                'ed_designation_id': designation.id,
                                'ed_workday_type_id': workday_type.id,
                                'ed_contract_hours': contract_hours,
                                'ed_work_reason_id': workreason.id,
                                'ed_contract_type_id': contract_type.id,
                                'ed_reduction_age': age,
                                'ed_reduction_health': health,
                                'ed_work_hours': work_hours,
                                'ed_class_hours': class_hours,
                                'notes': notes,
                                'wage': 0.0,
                                'company_id': company.id,
                            }
                            if not contract:
                                hr_contract_obj.create(contract_vals)
                            else:
                                contract.write(contract_vals)
                        if op_type == 'B':
                            # BAJA
                            if contract:
                                # termination_code = _format_info(line[21:24])
                                date_end = \
                                    fields.Datetime.to_string(
                                        datetime.strptime(
                                            _format_info(line[24:32]),
                                            '%d%m%Y'))
                                contract.write({
                                    'date_end': date_end,
                                })
        action = self.env.ref('hr.open_view_employee_list_my')
        return action.read()[0]
