# Copyright 2020 Daniel Campos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationExam(models.Model):
    _inherit = 'education.exam'

    sequence = fields.Integer('Sequence', default=10)

    @api.model
    def create(self, vals):
        res = super(EducationExam, self).create(vals)
        res.set_sequence_order()
        return res

    def set_sequence_order(self):
        for record in self:
            record.sequence = record.sequence + int(record.id) if record.sequence else int(record.id)
