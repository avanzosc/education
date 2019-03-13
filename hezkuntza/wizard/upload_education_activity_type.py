# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationActivityType(models.TransientModel):
    _name = 'upload.education.activity_type'
    _description = 'Wizard to Upload Education Other Activity Types'

    file = fields.Binary(
        string='Other Activity Types File (T07)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        activity_type_obj = self.env['education.activity_type']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:3])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[3:103]),
                        'description_eu': _format_info(line[103:203]),
                        'short_description': _format_info(line[203:223]),
                        'short_description_eu': _format_info(line[223:243]),
                    }
                    activity_types = activity_type_obj.search([
                        ('education_code', '=', education_code)])
                    if activity_types:
                        activity_types.write(vals)
                    else:
                        activity_type_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_activity_type')
        return action.read()[0]
