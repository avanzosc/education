# Copyright 2022 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    responsible = fields.Many2one('hr.employee', string='Responsible')
    competence_ids = fields.Many2many(
        comodel_name="education.competence", string="Competence")
    level_ids = fields.Many2many(
        comodel_name='education.level', string='Levels',
        relation='rel_education_level_survey',
        column1='survey_id', column2='level_id')
    education_course_ids = fields.Many2many(
        string="Education Courses",
        comodel_name="education.course")
    subject_ids = fields.Many2many(
        string="Education Subjects",
        comodel_name="education.subject")


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    responsible = fields.Many2one(
        comodel_name='hr.employee', string='Responsible',
        related='survey_id.responsible')
    average_grade = fields.Float(string='Average Grade')
    education_record_id = fields.Many2one(
        'education.record', string='Education Record')
    notebook_line_id = fields.Many2one(
        'education.notebook.line', string='Notebook Line')
    academic_year = fields.Many2one(
        comodel_name='education.academic_year', string='Academic Year',
        related='education_record_id.academic_year_id')
    evaluation = fields.Selection(
        'Evaluation', related='education_record_id.eval_type')
    description = fields.Char(
        'Description', related='education_record_id.display_name')
    subject_id = fields.Many2one(
        comodel_name='education.subject', string='Subject',
        related='education_record_id.subject_id')
    education_center = fields.Many2one(
        comodel_name='res.partner', string='Education Center',
        related='education_record_id.education_center_id')

    @api.onchange('quizz_score', 'user_input_line_ids')
    def compute_average_grade(self):
        for record in self:
            if record.education_record_id:
                record.average_grade = record.quizz_score/len(record.user_input_line_ids)
                record.education_record_id.set_numeric_mark(record.quizz_score)


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input_line"

    def save_lines(self, user_input_id, question, post, answer_tag):
        res = super(SurveyUserInputLine, self).save_lines(user_input_id, question, post, answer_tag)
        user_input = self.env['survey.user_input'].browse(user_input_id)
        user_input.compute_average_grade()
        return res