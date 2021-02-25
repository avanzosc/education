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
    passed = fields.Boolean(
        string="Passed", default=False,
        help="This field will determine if it the record is considered as"
             " passed or failed.")
    active = fields.Boolean(default=True)

    def _get_mark(self, numeric_value=False):
        if not numeric_value:
            numeric_value = 0.0
        return self.env["education.mark.numeric"].search([
            ("initial_mark", "<=", numeric_value),
            ("final_mark", ">=", numeric_value)], limit=1)
