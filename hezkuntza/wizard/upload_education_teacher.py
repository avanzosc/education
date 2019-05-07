# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationTeacher(models.TransientModel):
    _name = 'upload.education.teacher'
    _description = 'Wizard to Upload Teachers'

    file = fields.Binary(
        string='Teachers (T06)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        # classroom_obj = self.env[
        #     'education.classroom'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    line_type = _format_info(line[:1])
                    print(_format_info(line))
                    # if line_type == '1':
                    #     print(_format_info(line))
                        # colegio = _format_info(line[3:9])
                        # año = _format_info(line[9:13])
                    if line_type == '2':
                        op_type = _format_info(line[1:2])
                        print('tipo documento: {}'.format(
                            _format_info(line[2:6])))
                        print('documento: {}'.format(_format_info(line[6:21])))
                        if op_type == 'M':
                            # MODIFICACIÓN o ALTA
                            print(
                                'apel1: {}'.format(_format_info(line[21:71])))
                            print(
                                'apel2: {}'.format(_format_info(line[71:121])))
                            print('nombre: {}'.format(
                                _format_info(line[121:151])))
                            print('cargo: {}'.format(
                                _format_info(line[151:154])))
                            print('cargo2: {}'.format(
                                _format_info(line[154:157])))
                            print('otrocargo: {}'.format(
                                _format_info(line[157:160])))
                            print(
                                'dpto: {}'.format(_format_info(line[160:310])))
                            print(
                                'nomb: {}'.format(_format_info(line[310:312])))
                            print('jornada: {}'.format(_format_info(line[
                                                                    312:316])))
                            print('horas: {}'.format(
                                _format_info(line[316:321])))
                            print(
                                'lect: {}'.format(_format_info(line[321:326])))
                            print('mayor: {}'.format(
                                _format_info(line[326:327])))
                            print('salud: {}'.format(
                                _format_info(line[327:328])))
                            print(
                                'obs: {}'.format(_format_info(line[328:578])))
                            print('causa: {}'.format(
                                _format_info(line[578:582])))
                            print('fecha: {}'.format(
                                _format_info(line[582:590])))
                            print(
                                'tipo: {}'.format(_format_info(line[590:594])))
                            print('contra: {}'.format(
                                _format_info(line[594:599])))
                        if op_type == 'B':
                            # BAJA
                            print('cese: {}'.format(_format_info(line[21:24])))
                            print('fecha: {}'.format(_format_info(line[
                                                                  24:32])))
        #             education_code = _format_info(line[0:8])
        #             vals = {
        #                 'education_code': education_code,
        #                 'description': _format_info(line[8:58]),
        #                 'capacity': _format_info(line[58:61]),
        #             }
        #             classrooms = classroom_obj.search([
        #                 ('education_code', '=', education_code)])
        #             if classrooms:
        #                 classrooms.write(vals)
        #             else:
        #                 classroom_obj.create(vals)
        return True
        # action = self.env.ref('education.action_education_classroom')
        # return action.read()[0]
