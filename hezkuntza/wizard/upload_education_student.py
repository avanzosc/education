# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationStudent(models.TransientModel):
    _name = 'upload.education.student'
    _description = 'Wizard to Upload Student'

    file = fields.Binary(
        string='Students File (T27)', filters='*.txt')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        domain=[('educational_category', '=', 'school')], required=True)
    academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        required=True)

    def button_upload(self):
        lines = _read_binary_file(self.file)
        group_obj = self.env['education.group'].with_context(active_test=False)
        partner_obj = self.env['res.partner'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    group_code = _format_info(line[0:8])
                    group = group_obj.search([
                        ('education_code', '=', group_code),
                        ('center_id', '=', self.center_id.id),
                        ('academic_year_id', '=', self.academic_year_id.id),
                    ])
                    partner_code = _format_info(line[8:18])
                    student = partner_obj.search([
                        '|', ('education_code', '=', partner_code),
                        ('education_code', 'ilike', partner_code[1:]),
                        ('educational_category', '=', 'student'),
                    ], limit=1)
                    if group and student:
                        group.write({
                            'student_ids': [(4, student.id)],
                        })
        action = self.env.ref('education.action_education_group')
        return action.read()[0]
