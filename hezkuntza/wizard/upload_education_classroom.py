# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class UploadEducationClassroom(models.TransientModel):
    _name = 'upload.education.classroom'
    _description = 'Wizard to Upload Classrooms'

    file = fields.Binary(
        string='Classrooms (T06)', filters='*.txt')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        domain=[('educational_category', '=', 'school')], required=True)

    def button_upload(self):
        lines = _read_binary_file(self.file)
        classroom_obj = classrooms_list = self.env[
            'education.classroom'].with_context(active_test=False)
        # classroom_ids = []
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:8])
                    description = _format_info(line[8:58])
                    vals = {
                        'education_code': education_code,
                        'description': description,
                        'capacity': _format_info(line[58:61]),
                        'center_id': self.center_id.id,
                    }
                    classrooms = classroom_obj.search([
                        '|', ('education_code', '=', education_code),
                        ('description', '=', description),
                        ('center_id', '=', self.center_id.id),
                    ])
                    if classrooms:
                        if len(classrooms) != 1:
                            classrooms = classrooms.filtered(
                                lambda c: c.education_code ==
                                          education_code)
                        classrooms.write(vals)
                    else:
                        classrooms = classroom_obj.create(vals)
                classrooms_list |= classrooms
        if classrooms_list:
            classrooms_list.filtered(lambda c: not c.active).toggle_active()
            disable_classrooms = classroom_obj.search([
                ("center_id", "=", self.center_id.id),
                ("id", "not in", classrooms_list.ids),
                ("active", "=", True),
            ])
            disable_classrooms.toggle_active()
        action = self.env.ref("education.action_education_classroom")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("center_id", "=", self.center_id.id)],
            safe_eval(action.domain or '[]')
        ])
        context = safe_eval(action.context or '{}')
        context.update({
            "default_center_id": self.center_id.id,
            "active_test": False,
        })
        action_dict.update({
            "domain": domain,
            "context": context,
        })
        return action_dict
