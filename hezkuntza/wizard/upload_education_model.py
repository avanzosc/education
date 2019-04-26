# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationModel(models.TransientModel):
    _name = 'upload.education.model'
    _description = 'Wizard to Upload Educational Model'

    file = fields.Binary(
        string='Educational Models file (V55T35)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        model_obj = self.env['education.model'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:4])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[4:19]),
                        'description_eu': _format_info(line[19:34]),
                    }
                    models = model_obj.search([
                        ('education_code', '=', education_code)])
                    if models:
                        models.write(vals)
                    else:
                        model_obj.create(vals)
        action = self.env.ref('education.action_education_model')
        return action.read()[0]
