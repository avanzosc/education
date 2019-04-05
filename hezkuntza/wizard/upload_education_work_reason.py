# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationWorkReason(models.TransientModel):
    _name = 'upload.education.work_reason'
    _description = 'Wizard to Upload Education Work Reason'

    file = fields.Binary(
        string='Work Reasons File (T04)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        work_reason_obj = self.env['education.work_reason']
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
                        'short_description': _format_info(line[204:224]),
                        'short_description_eu': _format_info(line[224:244]),
                    }
                    work_reasons = work_reason_obj.search([
                        ('education_code', '=', education_code)])
                    if work_reasons:
                        work_reasons.write(vals)
                    else:
                        work_reason_obj.create(vals)
        action = self.env.ref('education.action_education_work_reason')
        return action.read()[0]
