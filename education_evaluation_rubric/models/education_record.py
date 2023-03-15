# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class EducationRecord(models.Model):
    _inherit = 'education.record'

    survey_input_id = fields.Many2one('survey.user_input', string='Survey Input')
    survey_id = fields.Many2one('survey.survey', compute='compute_survey')
    quizz_score = fields.Float(related='survey_input_id.quizz_score')

    def compute_survey(self):
        for record in self:
            record.survey_id = record.n_line_id.edited_survey_id.id if record.n_line_id.edited_survey_id else record.n_line_id.survey_id.id

    def create_survey_input(self):
        for record in self:
            if record.survey_id:
                record.survey_input_id = self.env['survey.user_input'].create({
                    'survey_id': record.survey_id.id,
                    'partner_id': record.student_id.id,
                    'responsible': record.teacher_id.id,
                    'notebook_line_id': record.n_line_id.id,
                    'exam_id': record.exam_id.id if record.exam_id else None,
                    'education_record_id': record.id,
                })

    def button_respond_survey(self):
        self.ensure_one()
        res = self.survey_input_id.button_respond_survey()
        res['target'] = 'new'
        return res

    def create(self, vals):
        res = super(EducationRecord, self).create(vals)
        res.create_survey_input()
        return res

    def set_numeric_mark(self, mark):
        for record in self:
            record.numeric_mark = mark
            if not record.behaviour_mark_id:
                record.behaviour_mark_id = self.env['education.mark.behaviour'].browse(1)

    def _onchange_survey_mark(self):
        if self.state != 'assessed':
            set_mark = self.quizz_score if self.survey_id.related_record_mark == 'quizz_score' else self.survey_input_id.average_grade
            self.set_numeric_mark(set_mark)

    def get_survey_url(self):
        for record in self:
            if record.survey_id and record.survey_input_id:
                url_get = record.button_respond_survey()
                return url_get.get('url', None)