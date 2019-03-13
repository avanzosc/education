# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationCourse(models.TransientModel):
    _name = 'upload.education.course'
    _description = 'Wizard to Upload Education Courses'

    file = fields.Binary(
        string='Courses File (V55T12)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        course_obj = self.env['education.course']
        level_obj = self.env['education.level']
        plan_obj = self.env['education.plan']
        field_obj = self.env['education.field']
        shift_obj = self.env['education.shift']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[24:28])
                    plan = plan_obj.search([
                        ('education_code', '=', _format_info(line[4:8]))])
                    level = level_obj.search([
                        ('education_code', '=', _format_info(line[12:16])),
                        ('plan_id', '=', plan.id),
                    ])
                    field = field_obj.search([
                        ('education_code', '=', _format_info(line[16:20]))])
                    shift = shift_obj.search([
                        ('education_code', '=', _format_info(line[20:24]))
                    ])
                    vals = {
                        'education_code': education_code,
                        'plan_id': plan.id,
                        'level_id': level.id,
                        'field_id': field.id,
                        'shift_id': shift.id,
                        'description': _format_info(line[28:78]),
                        'description_eu': _format_info(line[78:128]),
                    }
                    courses = course_obj.search([
                        ('education_code', '=', education_code),
                        ('plan_id', '=', plan.id),
                        ('level_id', '=', level.id),
                        ('field_id', '=', field.id),
                        ('shift_id', '=', shift.id)])
                    if courses:
                        courses.write(vals)
                    else:
                        course_obj.create(vals)
        action = self.env.ref('hezkuntza.action_education_course')
        return action.read()[0]
