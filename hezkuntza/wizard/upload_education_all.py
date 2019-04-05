# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class UploadEducationAll(models.TransientModel):
    _name = 'upload.education.all'
    _description = 'Wizard to Upload Education Data'

    file_designation_level = fields.Binary(
        string='Designation Levels File (061)', filters='*.txt')
    file_normal_position = fields.Binary(
        string='Positions file (070)', filters='*.txt')
    file_work_reason = fields.Binary(
        string='Work Reasons File (T04)', filters='*.txt')
    file_group_type = fields.Binary(
        string='Educational Group Types File (T05)', filters='*.txt')
    file_activity_type = fields.Binary(
        string='Other Activity Types File (T07)', filters='*.txt')
    file_level_task_type = fields.Binary(
        string='Task Type per Level File (T08)', filters='*.txt')
    file_level_workday_type = fields.Binary(
        string='Level and Workday Type Relation File (T09)', filters='*.txt')
    file_task_type = fields.Binary(
        string='Task Types File (T13)', filters='*.txt')
    file_other_position = fields.Binary(
        string='Other Positions file (T16)', filters='*.txt')
    file_workday_type = fields.Binary(
        string='Workday Types File (T30)', filters='*.txt')
    file_contract_type = fields.Binary(
        string='Contract Types File (T31)', filters='*.txt')
    file_language = fields.Binary(
        string='Languages File (T55)', filters='*.txt')
    file_level = fields.Binary(
        string='Levels File (V55T11)', filters='*.txt')
    file_course = fields.Binary(
        string='Courses File (V55T12)', filters='*.txt')
    file_field = fields.Binary(
        string='Study Fields File (V55T14)', filters='*.txt')
    file_level_course_subject = fields.Binary(
        string='Level / Course / Subject File (V55T25)', filters='*.txt')
    file_shift = fields.Binary(
        string='Class Shifts File (V55T32)', filters='*.txt')
    file_model = fields.Binary(
        string='Educational Models file (V55T35)', filters='*.txt')
    file_idtype = fields.Binary(
        string='ID Types File (V55T86)', filters='*.txt')
    file_subject = fields.Binary(
        string='Subjects File (V55T15W18T54_1)', filters='*.txt')
    file_level_field_subject = fields.Binary(
        string='Level / Field / Subject File (V55T15W18T54_2)',
        filters='*.txt')

    def button_upload(self):
        result = {}
        if self.file_designation_level:
            try:
                wiz = self.env['upload.education.designation_level'].create({
                    'file': self.file_designation_level,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_normal_position:
            try:
                wiz = self.env['upload.education.position'].create({
                    'file_normal': self.file_normal_position,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_work_reason:
            try:
                wiz = self.env['upload.education.work_reason'].create({
                    'file': self.file_work_reason,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_group_type:
            try:
                wiz = self.env['upload.education.group_type'].create({
                    'file': self.file_group_type,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_activity_type:
            try:
                wiz = self.env['upload.education.activity_type'].create({
                    'file': self.file_activity_type,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_task_type:
            try:
                wiz = self.env['upload.education.task_type'].create({
                    'file': self.file_task_type,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_other_position:
            try:
                wiz = self.env['upload.education.position'].create({
                    'file_other': self.file_other_position,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_workday_type:
            try:
                wiz = self.env['upload.education.workday_type'].create({
                    'file': self.file_workday_type,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_contract_type:
            try:
                wiz = self.env['upload.education.contract_type'].create({
                    'file': self.file_contract_type,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_language:
            try:
                wiz = self.env['upload.education.language'].create({
                    'file': self.file_language,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_level:
            try:
                wiz = self.env['upload.education.level'].create({
                    'file': self.file_level,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_course:
            try:
                wiz = self.env['upload.education.course'].create({
                    'file': self.file_course,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_field:
            try:
                wiz = self.env['upload.education.field'].create({
                    'file': self.file_field,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_shift:
            try:
                wiz = self.env['upload.education.shift'].create({
                    'file': self.file_shift,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_model:
            try:
                wiz = self.env['upload.education.model'].create({
                    'file': self.file_model,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_idtype:
            try:
                wiz = self.env['upload.education.id_type'].create({
                    'file': self.file_idtype,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_subject:
            try:
                wiz = self.env['upload.education.subject'].create({
                    'file': self.file_subject,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_level_task_type:
            try:
                wiz = self.env['upload.education.level.task_type'].create({
                    'file': self.file_level_task_type,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_level_workday_type:
            try:
                wiz = self.env['upload.education.level.workday_type'].create({
                    'file': self.file_level_workday_type,
                })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_level_course_subject:
            try:
                wiz = self.env[
                    'upload.education.level.course.subject'].create({
                        'file': self.file_level_course_subject,
                    })
                wiz.button_upload()
            except Exception:
                pass
        if self.file_level_field_subject:
            try:
                wiz = self.env['upload.education.level.field.subject'].create({
                    'file': self.file_level_field_subject,
                })
                wiz.button_upload()
            except Exception:
                pass
        return result
