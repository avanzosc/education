# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models, _


class EducationExamCheck(models.TransientModel):
    _name = 'education.exam.check'
    _description = 'Wizard to check is exam is closed'

    name = fields.Char(string='Mensaje')

    @api.multi
    def button_save(self):
        exams = self.env['education.exam'].browse(
            self.env.context.get('active_ids'))
        exams.action_close_exam()
    