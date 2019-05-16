# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info  # ,\
# _convert_time_str_to_float
from odoo import _, exceptions, fields, models
# from datetime import datetime


class UploadEducationTeacher(models.TransientModel):
    _name = 'upload.education.teacher'
    _description = 'Wizard to Upload Teachers'

    file = fields.Binary(
        string='Teachers (T06)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        partner_obj = self.env['res.partner'].with_context(active_test=False)
        employee_obj = self.env['hr.employee'].with_context(active_test=False)
        department_obj = self.env['hr.department'].with_context(
            active_test=False)
        user_obj = self.env['res.users'].with_context(active_test=False)
        # academic_year_obj = self.env[
        #     'education.academic_year'].with_context(active_test=False)
        idtype_obj = self.env[
            'education.idtype'].with_context(active_test=False)
        # position_obj = self.env[
        #     'education.position'].with_context(active_test=False)
        # designation_obj = self.env[
        #     'education.designation_level'].with_context(active_test=False)
        # workday_type_obj = self.env[
        #     'education.workday_type'].with_context(active_test=False)
        # contract_type_obj = self.env[
        #     'education.contract_type'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    line_type = _format_info(line[:1])
                    # if line_type == '1':
                    #     center_code = _format_info(line[3:9])
                    #     partner = partner_obj.search([
                    #         ('education_code', '=', center_code),
                    #         ('educational_category', '=', 'school'),
                    #     ])
                    #     year = _format_info(line[9:13])
                    #     academic_year = academic_year_obj.search([
                    #         ('name', 'ilike', '{}-'.format(year)),
                    #     ])
                    if line_type == '2':
                        op_type = _format_info(line[1:2])
                        id_type = idtype_obj.search([
                            ('education_code', '=', _format_info(line[2:6]))])
                        id_number = _format_info(line[6:21])
                        employee = employee_obj.search([
                            ('edu_idtype_id', '=', id_type.id),
                            ('identification_id', '=', id_number),
                        ])
                        user = (
                            employee.user_id or
                            user_obj.search([
                                ('vat', 'ilike', id_number),
                                ('edu_idtype_id', '=', id_type.id)]))
                        if op_type == 'M':
                            # MODIFICACIÓN o ALTA
                            lastname = _format_info(line[21:71])
                            lastname2 = _format_info(line[71:121])
                            firstname = _format_info(line[121:151])
                            fullname = partner_obj._get_computed_name(
                                lastname, firstname, lastname2)
                            # position1 = position_obj.search([
                            #     ('type', '=', 'normal'),
                            #     ('education_code', '=',
                            #      _format_info(line[151:154])),
                            # ])
                            # print('cargo: {}'.format(position1.display_name))
                            # position2 = position_obj.search([
                            #     ('type', '=', 'normal'),
                            #     ('education_code', '=',
                            #      _format_info(line[154:157])),
                            # ])
                            # print('cargo2: {}'.format(
                            # position2.display_name))
                            # position3 = position_obj.search([
                            #     ('type', '=', 'other'),
                            #     ('education_code', '=',
                            #      _format_info(line[157:160])),
                            # ])
                            # print('otrocargo: {}'.format(
                            #     position3.display_name))
                            department_name = _format_info(line[160:310])
                            department = department_obj.search([
                                ('name', '=', department_name)
                            ])
                            if not department:
                                department_obj.create({
                                    'name': department_name,
                                })
                            # dcode = '0{}'.format(_format_info(line[310:312]))
                            # designation = designation_obj.search([
                            #     ('education_code', '=', dcode),
                            # ])
                            # wcode = '00000{}'.format(
                            #         _format_info(line[312:316]))
                            # workday_type = workday_type_obj.search([
                            #     ('education_code', '=', wcode),
                            # ])
                            # workhours = _convert_time_str_to_float(
                            #     _format_info(line[316:321]))
                            # print(
                            #     'lect: {}'.format(
                            # _format_info(line[321:326])))
                            # print('mayor: {}'.format(
                            #     _format_info(line[326:327])))
                            # print('salud: {}'.format(
                            #     _format_info(line[327:328])))
                            # print(
                            #     'obs: {}'.format(
                            # _format_info(line[328:578])))
                            # print('causa: {}'.format(
                            #     _format_info(line[578:582])))
                            # date_start = \
                            #     fields.Datetime.to_string(
                            #         datetime.strptime(
                            #             _format_info(
                            # line[582:590]), '%d%m%Y'))
                            # print('fecha: {}'.format(
                            #     fields.Date.from_string(date_start)))
                            # contract_type = contract_type_obj.search([
                            #     ('education_code', '=',
                            #      _format_info(line[590:594])),
                            # ])
                            # print('tipo: {}'.format(
                            #     contract_type.display_name))
                            # print('contra: {}'.format(
                            #     _format_info(line[594:599])))
                            vals = {
                                'name': fullname,
                                'department_id': department.id,
                            }
                            if not user:
                                vals.update({
                                    'login': id_number,
                                    'vat': id_number,
                                    'edu_idtype_id': id_type.id,
                                })
                                user = user_obj.create(vals)
                            if not employee:
                                vals.update({
                                    'edu_idtype_id': id_type.id,
                                    'identification_id': id_number,
                                    'user_id': user.id,
                                    'gender': False,
                                    'marital': False,
                                })
                                employee_obj.create(vals)
                            else:
                                if not employee.user_id:
                                    vals.update({
                                        'user_id': user.id
                                    })
                                employee.write(vals)
                        # if op_type == 'B':
                        #     # BAJA
                        #     print('cese: {}'.format(
                        # _format_info(line[21:24])))
                        #     print('fecha: {}'.format(_format_info(line[
                        #                                           24:32])))
        return True
        # action = self.env.ref('education.action_education_classroom')
        # return action.read()[0]
