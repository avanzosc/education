# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationContractType(models.TransientModel):
    _name = 'upload.education.shift'
    _description = 'Wizard to Upload Class Shift'

    file = fields.Binary(
        string='Class Shifts File (V55T32)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        shift_obj = self.env['education.shift']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:4])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[4:24]),
                        'description_eu': _format_info(line[24:44]),
                    }
                    shifts = shift_obj.search([
                        ('education_code', '=', education_code)])
                    if shifts:
                        shifts.write(vals)
                    else:
                        shift_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_shift')
        return action.read()[0]
