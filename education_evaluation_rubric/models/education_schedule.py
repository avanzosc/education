# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

    rubric_questions_count = fields.Integer(
        'Rubric questions count', compute='_rubric_questions_count')

    def _rubric_questions_count(self):
        for record in self:
            domain = record._rubric_questions_domain()
            if len(domain) > 0:
                record.rubric_questions_count = self.env['survey.question'].search_count(domain)

    def _rubric_questions_domain(self):
        self.ensure_one()
        domain = []
        survey_ids = self.notebook_line_ids.mapped('edited_survey_id')
        if not survey_ids:
            n_line_survey_ids = self.notebook_line_ids.mapped('survey_id')
            survey_ids = self.env['survey.survey'].search([
                ('id', 'in', n_line_survey_ids.ids),
            ])
        if survey_ids:
            survey_question_ids = self.env['survey.question'].search([
                ('survey_id', 'in', survey_ids.ids),
            ])
            domain += [('id', 'in', survey_question_ids.ids)]
        return domain

    @api.multi
    def button_open_rubric_questions(self):
        self.ensure_one()
        domain = self._rubric_questions_domain()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule rubric questions'),
            'res_model': 'survey.question',
            'view_mode': 'tree,form',
            'domain': domain,
        }
