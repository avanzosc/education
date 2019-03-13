# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationIdType(models.TransientModel):
    _name = 'upload.education.idtype'
    _description = 'Wizard to Upload Education ID Types'

    file = fields.Binary(
        string='ID Types File (V55T86)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        idtype_obj = self.env['education.idtype']
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
                    idtypes = idtype_obj.search([
                        ('education_code', '=', education_code)])
                    if idtypes:
                        idtypes.write(vals)
                    else:
                        idtype_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_idtype')
        return action.read()[0]
