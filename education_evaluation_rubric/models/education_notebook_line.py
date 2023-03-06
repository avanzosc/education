# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo import exceptions
from odoo.exceptions import UserError


class EducationNotebookLine(models.Model):
    _inherit = 'education.notebook.line'

    eval_mode = fields.Selection(related='competence_id.eval_mode')
    course_ids = fields.Many2many(
        'education.course', string='Education Course', related="subject_id.course_ids")
    survey_id = fields.Many2one('survey.survey', string='Survey Template')
    edited_survey_id = fields.Many2one('survey.survey', string='Custom Survey Template')
    edited_survey_show = fields.Boolean(default=False, string='Custom Survey Show')
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

    @api.multi
    def button_create_custom_survey(self):
        for record in self:
            if record.survey_id:
                if record.survey_input_ids:
                    record.survey_input_ids.unlink()
                record.edited_survey_id = record.survey_id.copy({
                    'responsible': record.teacher_id.id,
                    'create_uid': self.env.uid,
                })
                # for page in record.sudo().survey_id.page_ids:
                #     page = page.copy({
                #         'survey_id': record.edited_survey_id.id,
                #     })
                record.edited_survey_id.title = record.survey_id.title + '(' + record.teacher_id.display_name + ')'
                record.record_ids.create_survey_input()
                record.edited_survey_show = True
                record.edited_survey_id.copy_survey_texts(record.survey_id.sudo())

    @api.onchange('survey_id')
    def _onchange_survey(self):
        for record in self:
            if record.survey_id:
                record.survey_id.responsible = record.teacher_id.user_id.partner_id.id

    @api.multi
    def button_open_all_survey_inputs(self):
        self.ensure_one()
        first_survey = self.env['survey.user_input'].search([
            ('id', 'in', self.survey_input_ids.ids)], order="id asc")
        res = first_survey[0].button_respond_survey()
        res['target'] = 'new'
        return res

    def get_survey_url(self):
        for record in self:
            if record.survey_id and record.competence_id.eval_mode == 'rubric':
                url_get = record.button_open_all_survey_inputs()
                return url_get.get('url', None)


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

    @api.multi
    def action_survey_user_input(self):
        self.ensure_one()
        action_rec = self.env.ref('survey.action_survey_user_input')
        action = action_rec.read()[0]
        action.update({
            'domain': [('exam_id', '=', self.id)],
        })
        return action

    def get_survey_url(self):
        for record in self:
            if record.survey_id and record.survey_input_ids:
                url_get = record.button_open_all_survey_inputs()
                return url_get.get('url', None)
