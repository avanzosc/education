# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationField(models.TransientModel):
    _name = 'upload.education.field'
    _description = 'Wizard to Upload Education Fields'

    file = fields.Binary(
        string='Study Fields File (V55T14)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        field_obj = self.env['education.field']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:4])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[4:54]),
                        'description_eu': _format_info(line[54:104]),
                    }
                    fields = field_obj.search([
                        ('education_code', '=', education_code)])
                    if fields:
                        fields.write(vals)
                    else:
                        field_obj.create(vals)
        action = self.env.ref('education.action_education_field')
        return action.read()[0]
