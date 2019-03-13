# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationContractType(models.TransientModel):
    _name = 'upload.education.task_type'
    _description = 'Wizard to Upload Education Task Type'

    file = fields.Binary(
        string='Task Types File (T13)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        task_type_obj = self.env['education.task_type']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[1:5])
                    vals = {
                        'type': _format_info(line[0:1]),
                        'education_code': education_code,
                        'tutoring': _format_info(line[5:6]),
                        'description': _format_info(line[6:256]),
                        'description_eu': _format_info(line[256:506]),
                        'level': _format_info(line[506:507]),
                        'other_activities': _format_info(line[507:508]),
                    }
                    task_types = task_type_obj.search([
                        ('education_code', '=', education_code)])
                    if task_types:
                        task_types.write(vals)
                    else:
                        task_type_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_task_type')
        return action.read()[0]
