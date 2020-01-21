# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EducationNumericMark(models.Model):
    _name = "education.mark.numeric"
    _description = "Numeric Mark"
    _order = 'initial_mark DESC, final_mark DESC, name'

    name = fields.Char(string="Name", required=True, translate=True)
    reduced_name = fields.Char(string="Reduced Name")
    initial_mark = fields.Float(string="Initial Mark", required=True)
    final_mark = fields.Float(string="Final Mark", required=True)
