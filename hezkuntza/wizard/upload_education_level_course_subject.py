# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationLevelFieldSubject(models.TransientModel):
    _name = 'upload.education.level.course.subject'
    _description = 'Wizard to Upload Education Level, Course and Subject ' \
                   'Relation'

    file = fields.Binary(
        string='Level / Course / Subject File (V55T25)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        plan_obj = self.env['education.plan'].with_context(active_test=False)
        level_obj = self.env['education.level'].with_context(active_test=False)
        course_obj = self.env[
            'education.course'].with_context(active_test=False)
        subject_obj = self.env[
            'education.subject'].with_context(active_test=False)
        relation_obj = self.env[
            'education.level.course.subject'].with_context(active_test=False)
        if not lines and not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    plan = plan_obj.search([
                        ('education_code', '=', _format_info(line[4:8]))])
                    level = level_obj.search([
                        ('education_code', '=', _format_info(line[0:4])),
                        ('plan_id', '=', plan.id)])
                    courses = course_obj.search([
                        ('education_code', '=', _format_info(line[8:12])),
                        ('level_id', '=', level.id),
                        ('plan_id', '=', plan.id)])
                    subject = subject_obj.search([
                        ('education_code', '=', _format_info(line[12:20]))])
                    for course in courses:
                        vals = {
                            'level_id': level.id,
                            'plan_id': plan.id,
                            'course_id': course.id,
                            'subject_id': subject.id,
                        }
                        relations = relation_obj.search([
                            ('level_id', '=', level.id),
                            ('plan_id', '=', plan.id),
                            ('course_id', '=', course.id),
                            ('subject_id', '=', subject.id)])
                        if not relations:
                            relation_obj.create(vals)
        action = self.env.ref('education.action_education_subject')
        return action.read()[0]
