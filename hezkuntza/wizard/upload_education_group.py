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
        group_obj = self.env['education.group'].with_context(active_test=False)
        plan_obj = self.env['education.plan'].with_context(active_test=False)
        level_obj = self.env['education.level'].with_context(active_test=False)
        field_obj = self.env['education.field'].with_context(active_test=False)
        classroom_obj = self.env[
            'education.classroom'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    line_type = _format_info(line[:1])
                    # print(_format_info(line))
                    if line_type == '1':
                        center_code = _format_info(line[3:9])
                        print('Center Code: {}'.format(center_code))
                        partner = partner_obj.search([
                            ('education_code', '=', center_code)])
                        # año = _format_info(line[9:13])
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
                        classroom = classroom_obj.search([
                            ('education_code', '=',
                             _format_info(line[539:547])),
                            ('center_id', '=', partner.id),
                        ])
                        vals = {
                            'center_id': partner.id,
                            'education_code': group_code,
                            'description': _format_info(line[9:59]),
                            'plan_id': plan.id,
                            'level_id': level.id,
                            'field_id': field.id,
                            'classroom_id': classroom.id
                        }
                        groups = group_obj.search([
                            ('education_code', '=', group_code),
                            ('center_id', '=', partner.id)])
                        if groups:
                            groups.write(vals)
                        else:
                            group_obj.create(vals)
                        shift = _format_info(line[71:75])
                        course = _format_info(line[75:79])
                        model = _format_info(line[79:83])
                        group_type = _format_info(line[83:87])
                        calendar = _format_info(line[87:95])
                        start = 95
                        for i in range(0, 10):
                            end = start + 4
                            doc_type = _format_info(line[start:end])
                            start = end + 15
                            doc = _format_info(line[end:start])
                            print('document: [{}] {}'.format(doc_type, doc))
                        student_count = _format_info(line[285:289])
                        comments = _format_info(line[289:539])
                        classroom = _format_info(line[539:547])
                    if line_type == '3':
                        group_code = _format_info(line[1:9])
                        session = _format_info(line[9:11])
                        weekday = _format_info(line[11:12])
                        start = _format_info(line[12:17])
                        end = _format_info(line[17:22])
                        recess = _format_info(line[22:23])
        action = self.env.ref('education.action_education_group')
        return action.read()[0]
