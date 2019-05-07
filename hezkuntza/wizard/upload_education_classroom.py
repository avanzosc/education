# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationClassroom(models.TransientModel):
    _name = 'upload.education.classroom'
    _description = 'Wizard to Upload Classrooms'

    file = fields.Binary(
        string='Classrooms (T06)', filters='*.txt')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        domain=[('educational_category', '=', 'school')])

    def button_upload(self):
        lines = _read_binary_file(self.file)
        classroom_obj = self.env[
            'education.classroom'].with_context(active_test=False)
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:8])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[8:58]),
                        'capacity': _format_info(line[58:61]),
                        'center_id': self.center_id.id,
                    }
                    classrooms = classroom_obj.search([
                        ('education_code', '=', education_code),
                        ('center_id', '=', self.center_id.id),
                    ])
                    if classrooms:
                        classrooms.write(vals)
                    else:
                        classroom_obj.create(vals)
        action = self.env.ref('education.action_education_classroom')
        return action.read()[0]
