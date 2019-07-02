# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info, \
    _convert_time_str_to_float
from odoo import _, exceptions, fields, models
from odoo.addons.resource_education.models.resource_calendar import\
    EDUCATION_DAYOFWEEK_CODE


class UploadEducationGroup(models.TransientModel):
    _name = 'upload.education.resource'
    _description = 'Wizard to Upload Resources'

    file = fields.Binary(
        string='Resources', filters='*.txt')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        domain=[('educational_category', '=', 'school')], required=True)

    def button_upload(self):
        lines = _read_binary_file(self.file)
        calendar_obj = self.env['resource.calendar']
        attendance_obj = self.env['resource.calendar.attendance']
        dayofweek_dict = dict(map(reversed, EDUCATION_DAYOFWEEK_CODE.items()))
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    line_type = _format_info(line[:1])
                    if line_type == '1':
                        education_code = _format_info(line[1:9])
                        vals = {
                            'education_code': education_code,
                            'name': _format_info(line[9:59]),
                            'attendance_ids': [],
                            'center_id': self.center_id.id,
                        }
                        calendar = calendar_obj.search([
                            ('education_code', '=', education_code),
                            ('center_id', '=', self.center_id.id)
                        ])
                        if not calendar:
                            calendar = calendar_obj.create(vals)
                    elif line_type == '2' and calendar:
                        dayofweek = dayofweek_dict.get(
                            int(_format_info(line[3:4])))
                        daily_hour = int(_format_info(line[1:3]))
                        vals = {
                            'calendar_id': calendar.id,
                            'name': '{}{}{}'.format(
                                education_code, dayofweek, daily_hour),
                            'dayofweek': dayofweek,
                            'hour_from': _convert_time_str_to_float(
                                _format_info(line[4:9])),
                            'hour_to': _convert_time_str_to_float(
                                _format_info(line[9:14])),
                            'recess': _format_info(line[14:15]) == '1',
                        }
                        attendances = attendance_obj.search([
                            ('calendar_id', '=', calendar.id),
                            ('dayofweek', '=', dayofweek),
                            ('daily_hour', '=', daily_hour),
                        ])
                        if attendances:
                            attendances.write(vals)
                        else:
                            attendance_obj.create(vals)
        action = self.env.ref('resource.action_resource_calendar_form')
        return action.read()[0]
