# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationClassroom(models.Model):
    _name = 'education.classroom'
    _inherit = 'education.data'
    _description = 'Classroom'

    capacity = fields.Integer(string='Seating Capacity')
    center_id = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        required=True)

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            result.append((record.id, '[{}] {} ({})'.format(
                record.education_code, record.description,
                record.center_id.name)))
        return result
