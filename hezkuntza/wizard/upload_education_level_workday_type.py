# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationLevelWorkdayType(models.TransientModel):
    _name = 'upload.education.level.workday_type'
    _description = 'Wizard to Upload Education Level and Workday Type Relation'

    file = fields.Binary(
        string='Level and Workday Type Relation File (T09)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        relation_obj = self.env['education.level.workday_type']
        academic_year_obj = self.env['education.academic_year']
        workday_type_obj = self.env['education.workday_type']
        level_obj = self.env['education.level']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    academic_year_code = _format_info(line[0:9])
                    academic_year = academic_year_obj.search([
                        ('name', '=', academic_year_code)])
                    if not academic_year:
                        academic_year = academic_year_obj.create({
                            'name': academic_year_code,
                        })
                    workday_type = workday_type_obj.search([
                        ('education_code', '=', _format_info(line[9:18]))])
                    levels = level_obj.search([
                        ('education_code', '=', _format_info(line[18:22]))
                    ])
                    for level in levels:
                        vals = {
                            'academic_year_id': academic_year.id,
                            'workday_type_id': workday_type.id,
                            'level_id': level.id,
                            'dedicated_working_day': _format_info(line[22:27]),
                            'school_working_day': _format_info(line[27:32])
                        }
                        relations = relation_obj.search([
                            ('academic_year_id', '=', academic_year.id),
                            ('workday_type_id', '=', workday_type.id),
                            ('level_id', '=', level.id)])
                        if relations:
                            relations.write(vals)
                        else:
                            relation_obj.create(vals)
        action = self.env.ref('education.action_education_level')
        return action.read()[0]
