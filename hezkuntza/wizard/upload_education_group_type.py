# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationGroupType(models.TransientModel):
    _name = 'upload.education.group_type'
    _description = 'Wizard to Upload Educational Group Types'

    file = fields.Binary(
        string='Educational Group Types File (T05)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        group_type_obj = self.env['education.group_type']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:4])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[4:104]),
                        'description_eu': _format_info(line[104:204]),
                    }
                    group_types = group_type_obj.search([
                        ('education_code', '=', education_code)])
                    if group_types:
                        group_types.write(vals)
                    else:
                        group_type_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_group_type')
        return action.read()[0]
