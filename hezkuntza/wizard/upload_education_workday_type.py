# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationWorkdayType(models.TransientModel):
    _name = 'upload.education.workday_type'
    _description = 'Wizard to Upload Education Type of Workday'

    file = fields.Binary(
        string='Workday Types File (T30)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        workday_type_obj = self.env['education.workday_type']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:9])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[9:109]),
                        'description_eu': _format_info(line[109:209]),
                        'short_description': _format_info(line[209:229]),
                        'short_description_eu': _format_info(line[229:249]),
                    }
                    workday_types = workday_type_obj.search([
                        ('education_code', '=', education_code)])
                    if workday_types:
                        workday_types.write(vals)
                    else:
                        workday_type_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_workday_type')
        return action.read()[0]
