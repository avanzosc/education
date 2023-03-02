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
        set_mark = self.quizz_score if self.related_record_mark == 'quizz_score' else self.average_grade
        self.set_numeric_mark(set_mark)


class EducationExam(models.Model):
    _inherit = 'education.exam'

    survey_input_ids = fields.Many2many(
        string="Survey Inputs",
        comodel_name="survey.user_input",
        relation="survey_input_exam_rel",
        column1="exam_id",
        column2="input_id",
        compute="_compute_survey_input"
    )
    survey_input_count = fields.Integer('Survey input count', compute="_compute_survey_input_count")
    survey_id = fields.Many2one('survey.survey', compute='compute_survey')

    def compute_survey(self):
        for record in self:
            record.survey_id = record.n_line_id.edited_survey_id.id if record.n_line_id.edited_survey_id else record.n_line_id.survey_id.id

    def _compute_survey_input(self):
        for record in self:
            record.survey_input_ids = self.env['survey.user_input'].search([
                ('exam_id', '=', record.id)
            ])

    def _compute_survey_input_count(self):
        for record in self:
            record.survey_input_count = len(record.survey_input_ids)

    @api.multi
    def button_open_all_survey_inputs(self):
        self.ensure_one()
        first_survey = self.env['survey.user_input'].search([
            ('id', 'in', self.survey_input_ids.ids)], order="id asc")
        res = first_survey[0].button_respond_survey()
        res['target'] = 'new'
        return res
