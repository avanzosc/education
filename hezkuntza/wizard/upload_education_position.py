# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationPosition(models.TransientModel):
    _name = 'upload.education.position'
    _description = 'Wizard to Upload Education Position'

    file_normal = fields.Binary(
        string='Positions file (070)', filters='*.txt')
    file_other = fields.Binary(
        string='Other Positions file (T16)', filters='*.txt')

    def button_upload(self):
        normal_lines = _read_binary_file(self.file_normal)
        other_lines = _read_binary_file(self.file_other)
        position_obj = self.env['education.position']
        if not normal_lines and not other_lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in normal_lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:3])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[3:103]),
                        'description_eu': _format_info(line[103:203]),
                        'type': 'normal',
                    }
                    positions = position_obj.search([
                        ('education_code', '=', education_code),
                        ('type', '=', 'normal')])
                    if positions:
                        positions.write(vals)
                    else:
                        position_obj.create(vals)
            for line in other_lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:3])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[3:103]),
                        'description_eu': _format_info(line[103:203]),
                        'type': 'other',
                    }
                    positions = position_obj.search([
                        ('education_code', '=', education_code),
                        ('type', '=', 'other')])
                    if positions:
                        positions.write(vals)
                    else:
                        position_obj.create(vals)
        action = self.env.ref('education.action_education_position')
        return action.read()[0]
