# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationLevel(models.TransientModel):
    _name = 'upload.education.level'
    _description = 'Wizard to Upload Education Levels'

    file = fields.Binary(
        string='Levels File (V55T11)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        level_obj = self.env['education.level']
        plan_obj = self.env['education.plan']
        if not lines and not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:4])
                    plan = plan_obj.search([
                        ('education_code', '=', _format_info(line[4:8]))])
                    vals = {
                        'education_code': education_code,
                        'plan_id': plan.id,
                        'description': _format_info(line[8:58]),
                        'description_eu': _format_info(line[58:108]),
                        'short_description': _format_info(line[108:128]),
                        'short_description_eu': _format_info(line[128:148]),
                    }
                    levels = level_obj.search([
                        ('education_code', '=', education_code),
                        ('plan_id', '=', plan.id)])
                    if levels:
                        levels.write(vals)
                    else:
                        level_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_level')
        return action.read()[0]
