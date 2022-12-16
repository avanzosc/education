# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo import exceptions


class EducationNotebookLine(models.Model):
    _inherit = 'education.notebook.line'

    eval_mode = fields.Selection(related='competence_id.eval_mode')
    survey_id = fields.Many2one('survey.survey', string='Survey Template')
    survey_input_ids = fields.Many2many(
        string="Survey Inputs",
        comodel_name="survey.user_input",
        relation="survey_input_notebook_line_rel",
        column1="notebook_id",
        column2="input_id",
        compute="_compute_survey_input")
    survey_input_count = fields.Integer('Survey input count', compute="_compute_survey_input_count")

    def _compute_survey_input(self):
        for record in self:
            record.survey_input_ids = self.env['survey.user_input'].search([
                ('notebook_line_id', '=', record.id)
            ])

    def _compute_survey_input_count(self):
        for record in self:
            record.survey_input_count = len(record.survey_input_ids)

    @api.multi
    def action_survey_user_input(self):
        self.ensure_one()
        action_rec = self.env.ref('survey.action_survey_user_input')
        action = action_rec.read()[0]
        action.update({
            'domain': [('notebook_line_id', '=', self.id)],
        })
        return action

    @api.multi
    def button_create_student_records(self):
        for record in self:
            if record.eval_mode == 'rubric' and not record.survey_id:
                raise exceptions.ValidationError('Please Select Survey for Rubric Competence')

        super(EducationNotebookLine, self).button_create_student_records()

    @api.onchange('survey_id')
    def _onchange_survey(self):
        for record in self:
            if record.survey_id:
                record.survey_id.responsible = record.teacher_id.user_id.partner_id.id
