# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationSubject(models.TransientModel):
    _name = 'upload.education.subject'
    _description = 'Wizard to Upload Subjects'

    file = fields.Binary(
        string='Subjects File (V55T15W18T54_1)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        subject_obj = self.env['education.subject']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:8])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[8:108]),
                        'description_eu': _format_info(line[108:208]),
                        'short_description': _format_info(line[208:228]),
                        'short_description_eu': _format_info(line[228:248]),
                        'min_description': _format_info(line[248:252]),
                        'min_description_eu': _format_info(line[252:256]),
                        'type': _format_info(line[256:260]),
                    }
                    subjects = subject_obj.search([
                        ('education_code', '=', education_code)])
                    if subjects:
                        subjects.write(vals)
                    else:
                        subject_obj.create(vals)
        action = self.env.ref('education.action_education_subject')
        return action.read()[0]
