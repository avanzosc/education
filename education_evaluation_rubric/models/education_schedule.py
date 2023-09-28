# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

    rubric_questions_count = fields.Integer(
        'Rubric questions count', compute='_compute_rubric_questions_count')

    def _compute_rubric_questions_count(self):
        question_obj = self.env['survey.question']
        for record in self:
            domain = record._rubric_questions_domain()
            if len(domain) > 0:
                record.rubric_questions_count = question_obj.search_count(domain)

    def _rubric_questions_domain(self):
        self.ensure_one()
        domain = []
        surveys = self.env["survey.survey"]
        for exam in self.exam_ids.filtered(lambda e: e.edited_survey_id or e.survey_id):
            surveys |= exam.edited_survey_id or exam.survey_id
        if surveys:
            domain += [('id', 'in', surveys.mapped("page_ids.question_ids").ids)]
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
