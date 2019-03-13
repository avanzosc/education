# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationLevelTaskType(models.TransientModel):
    _name = 'upload.education.level.task_type'
    _description = 'Wizard to Upload Education Level and Task Type Relation'

    file = fields.Binary(
        string='Task Type per Level File (T08)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        task_type_obj = self.env['education.task_type']
        level_obj = self.env['education.level']
        plan_obj = self.env['education.plan']
        relations = {}
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    task_type_code = _format_info(line[0:4])
                    level_code = _format_info(line[4:8])
                    plan_code = _format_info(line[8:12])
                    plan = plan_obj.search([
                        ('education_code', '=', plan_code)])
                    level = level_obj.search([
                        ('education_code', '=', level_code),
                        ('plan_id', '=', plan.id)])
                    if task_type_code not in relations:
                        relations[task_type_code] = []
                    if level:
                        relations[task_type_code].append(level.id)
            for task_type_key in relations.keys():
                task_type = task_type_obj.search([
                    ('education_code', '=', task_type_key)
                ])
                if task_type:
                    task_type.write({
                        'level_ids': [(6, 0, relations[task_type_key])]
                    })
        action = self.env.ref('hezkuntza.action_education_level')
        return action.read()[0]
