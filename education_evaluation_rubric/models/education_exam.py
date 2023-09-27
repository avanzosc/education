# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationExam(models.Model):
    _inherit = 'education.exam'

    survey_id = fields.Many2one(comodel_name='survey.survey', string='Survey Template')
    edited_survey_id = fields.Many2one(
        comodel_name='survey.survey', string="Custom Survey Template")
    edited_survey_show = fields.Boolean(default=False, string='Show Custom Survey')
    is_rubric = fields.Boolean(default=False, string='Is Rubric Exam')
    # survey_input_ids = fields.Many2many(
    #     string="Survey Responses",
    #     comodel_name="survey.user_input",
    #     relation="survey_input_exam_rel",
    #     column1="exam_id",
    #     column2="input_id",
    #     compute="_compute_survey_input")
    survey_input_ids = fields.One2many(
        comodel_name="survey.user_input", inverse_name="exam_id",
        string="Survey Responses")
    survey_input_count = fields.Integer(
        string="# Survey Responses", compute="_compute_survey_input")
    missing_survey_inputs = fields.Boolean(
        string="Missing Survey Responses", compute="_compute_missing_survey_inputs"
    )

    def _compute_survey_input(self):
        for record in self:
            record.survey_input_count = len(record.survey_input_ids)

    def _compute_missing_survey_inputs(self):
        for record in self:
            missing_inputs = False
            if (record.is_rubric and
                not all([bool(r.survey_input_id) for r in record.record_ids])):
                    missing_inputs = True
            record.missing_survey_inputs = missing_inputs

    def button_create_missing_survey_inputs(self):
        for record in self:
            if record.is_rubric and (record.edited_survey_id or record.survey_id):
                missing_inputs = record.record_ids.filtered(
                    lambda r: not r.survey_input_id)
                missing_inputs.create_survey_input(
                    record.edited_survey_id or record.survey_id)

    @api.multi
    def action_survey_user_input(self):
        self.ensure_one()
        action_rec = self.env.ref('survey.action_survey_user_input')
        action = action_rec.read()[0]
        action.update({
            'domain': [('exam_id', '=', self.id)],
        })
        return action

    @api.multi
    def action_generate_record(self):
        for record in self.filtered(lambda e: e.state in ('draft', 'progress')):
            if record.is_rubric and not (record.survey_id or record.edited_survey_id):
                raise ValidationError(
                    _('Please Select Survey for Rubric Competence'))
        super(EducationExam, self).action_generate_record()

    @api.multi
    def button_create_custom_survey(self):
        for record in self:
            if record.survey_id:
                if record.survey_input_ids:
                    record.survey_input_ids.unlink()
                record.edited_survey_id = record.survey_id.copy(default={
                    "responsible": record.teacher_id.id,
                    "create_uid": self.env.uid,
                    "title": "{} ({})".format(record.survey_id.title,
                                              record.teacher_id.display_name)
                })
                # for page in record.sudo().survey_id.page_ids:
                #     page = page.copy({
                #         'survey_id': record.edited_survey_id.id,
                #     })
                record.record_ids.create_survey_input(record.edited_survey_id)
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
        first_survey = self.env["survey.user_input"].search([
            ("id", "in", self.survey_input_ids.ids),
            ("state", "!=", "done")
        ], order="id asc")
        res = first_survey[:1].button_respond_survey()
        res["target"] = 'new'
        return res

    def get_survey_url(self):
        self.ensure_one()
        url_get = self.button_open_all_survey_inputs()
        return url_get.get("url", None)
