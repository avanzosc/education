# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationLanguage(models.TransientModel):
    _name = 'upload.education.language'
    _description = 'Wizard to Upload Languages'

    file = fields.Binary(
        string='Languages File (T55)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        language_obj = self.env[
            'education.language'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:2])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[2:102]),
                        'description_eu': _format_info(line[102:202]),
                        'short_description': _format_info(line[202:206]),
                        'short_description_eu': _format_info(line[206:210]),
                    }
                    languages = language_obj.search([
                        ('education_code', '=', education_code)])
                    if languages:
                        languages.write(vals)
                    else:
                        language_obj.create(vals)
        action = self.env.ref('education.action_education_language')
        return action.read()[0]
