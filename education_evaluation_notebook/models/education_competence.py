# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationCompetence(models.Model):
    _name = "education.competence"
    _description = "Education Competence"

    code = fields.Char(
        string="Code", help="This code is used for academic record report")
    name = fields.Char(string="Name", required=True, translate=True)
    eval_mode = fields.Selection(selection=[
        ("numeric", "Numeric"),
        ("behaviour", "Behaviour"),
        ("both", "Both")],
        string="Evaluation Mode", default="numeric", required=True)
    evaluation_check = fields.Boolean(
        string="Evaluation Competence", copy=False)
    global_check = fields.Boolean(string="Global Competence", copy=False)
    min_mark = fields.Float(string="Min. Mark", default=0.0, copy=False)
    max_mark = fields.Float(string="Max. Mark", default=10.0, copy=False)
    passed_mark = fields.Float(
        string="Min. Mark to Pass", default=5.0, copy=False)

    @api.constrains("code")
    def _check_code_length(self):
        for competence in self.filtered("code"):
            if len(competence.code) > 3:
                raise ValidationError(
                    _("Code must have a length of 3 characters "))

    @api.constrains("evaluation_check")
    def _check_evaluation_check(self):
        eval_check = self.search([("evaluation_check", "=", True)])
        if len(eval_check) > 1:
            raise ValidationError(
                _("There can only be one evaluation competence."))

    @api.constrains("global_check")
    def _check_global_check(self):
        global_check = self.search([("global_check", "=", True)])
        if len(global_check) > 1:
            raise ValidationError(
                _("There can only be one global competence."))
