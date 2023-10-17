# Copyright 2021 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EducationRecord(models.Model):
    _inherit = "education.record"

    survey_input_id = fields.Many2one(
        comodel_name="survey.user_input", string="Survey Input")
    survey_input_state = fields.Selection(
        string="Survey Response State", related="survey_input_id.state"
    )
    survey_id = fields.Many2one(
        comodel_name="survey.survey", compute="_compute_survey")
    quizz_score = fields.Float(related="survey_input_id.quizz_score")

    @api.depends("exam_id", "exam_id.edited_survey_id", "exam_id.survey_id")
    def _compute_survey(self):
        for record in self:
            record.survey_id = (record.exam_id and
                                (record.exam_id.edited_survey_id or
                                 record.exam_id.survey_id))

    def create_survey_input(self, survey):
        user_input_obj = self.env["survey.user_input"]
        if not survey:
            return
        for record in self:
            record.survey_input_id = user_input_obj.create({
                "survey_id": survey.id,
                "partner_id": record.student_id.id,
                "responsible": record.teacher_id.id,
                "notebook_line_id": record.n_line_id.id,
                "exam_id": record.exam_id.id if record.exam_id else None,
                "education_record_id": record.id,
            })

    def button_respond_survey(self):
        self.ensure_one()
        res = self.survey_input_id.button_respond_survey()
        res["target"] = "new"
        return res

    def create(self, vals):
        res = super(EducationRecord, self).create(vals)
        if vals.get("exam_id"):
            exam = self.env["education.exam"].browse(vals.get("exam_id"))
            res.create_survey_input(exam.edited_survey_id or exam.survey_id)
        return res

    def set_numeric_mark(self, mark):
        for record in self:
            record.numeric_mark = mark
            if not record.behaviour_mark_id:
                record.behaviour_mark_id = self.env["education.mark.behaviour"].browse(1)

    def _onchange_survey_mark(self):
        if self.state != "assessed":
            set_mark = self.compute_numeric_mark()
            if set_mark:
                self.set_numeric_mark(set_mark)

    def compute_numeric_mark(self):
        self.ensure_one()
        ret_value = 0.0
        survey = self.survey_input_id.survey_id
        if survey.related_record_mark == "quizz_score":
            ret_value = self.quizz_score
        elif survey.related_record_mark == "average_grade":
            ret_value = self.survey_input_id.average_grade
        elif survey.related_record_mark == "maximum_average":
            self.survey_input_id.update_line_value_suggested()
            max_value = survey.mapped("page_ids").mapped("question_ids").mapped("labels_ids").sorted(
                key=lambda m: m.quizz_mark, reverse=True)[0]
            max_points = max_value.quizz_mark * len(survey.mapped("page_ids").mapped("question_ids").mapped("labels_ids_2"))
            quizz_score = sum(self.survey_input_id.user_input_line_ids.mapped("quizz_mark"))
            ret_value = quizz_score / max_points * 10
            if 0 > ret_value or 10 < ret_value:
                ret_value = None
        return ret_value

    def get_survey_url(self):
        self.ensure_one()
        if not self.survey_input_id:
            return UserError(_("No survey user input to show."))
        url_get = self.button_respond_survey()
        return url_get.get("url", None)

