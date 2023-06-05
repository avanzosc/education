# Copyright 2022 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    responsible = fields.Many2one('hr.employee', string='Responsible Teacher')
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
    is_base_survey = fields.Boolean('Is base survey')
    related_record_mark = fields.Selection(
        string='Records inherit mark',
        selection=[
            ('quizz_score', 'Quizz Score'),
            ('average_grade', 'Average Grade'),
            ('maximum_average', 'Maximum Average Grade'),
        ],
        default='quizz_score', required=True,
        help='Select whether to relate quizz_mark or average_grade on education record numeric marks.')

    def copy_survey_texts(self, original_survey):
        self.ensure_one()
        if original_survey.page_ids and original_survey.page_ids.question_ids:
            original_survey_texts = original_survey.mapped('page_ids').mapped('question_ids').mapped('survey_text_ids')
            for page in self.page_ids:
                for question in page.question_ids:
                    for label in question.labels_ids:
                        for label2 in question.labels_ids_2:
                            survey_text = original_survey_texts.filtered(
                                lambda t: t.label_id_1.value == label.value and t.label_id_2.value == label2.value)
                            self.env['survey.question.text'].create({
                                'question_id': question.id,
                                'label_id_1': label.id,
                                'label_id_2': label2.id,
                                'text': survey_text.text,
                            })

    def write(self, vals):
        res = super().write(vals)
        for record in self.user_input_ids.mapped('education_record_id'):
            record._onchange_survey_mark()
        return res


class SurveyPage(models.Model):
    _inherit = "survey.page"

    responsible = fields.Many2one('hr.employee', string='Responsible Teacher', related="survey_id.responsible")

    level_ids = fields.Many2many(
        comodel_name='education.level',
        related="survey_id.level_ids")

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    responsible = fields.Many2one(
        comodel_name='hr.employee', string='Responsible',
        compute='compute_survey_input_responsible')
    average_grade = fields.Float(string='Average Grade')
    education_record_id = fields.Many2one(
        'education.record', string='Education Record')
    notebook_line_id = fields.Many2one(
        'education.notebook.line', string='Notebook Line', ondelete='cascade')
    exam_id = fields.Many2one(
        'education.exam', string='Education Exam', ondelete='cascade')
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
    record_state = fields.Selection(
        'Education Record Status', related='education_record_id.state')

    def compute_survey_input_responsible(self):
        for record in self:
            record.responsible = record.education_record_id.teacher_id.id if record.education_record_id else record.survey_id.responsible.id

    @api.onchange('quizz_score', 'user_input_line_ids')
    def compute_average_grade(self):
        self_ids = self.ids or self._origin.ids
        records = self.env['survey.user_input'].browse(self_ids)
        for record in records:
            if record.education_record_id:
                record.average_grade = record.quizz_score/len(record.user_input_line_ids) if record.quizz_score else 0.0

    @api.depends('user_input_line_ids.quizz_mark')
    def _compute_quizz_score(self):
        for user_input in self:
            quizz_score = 0
            if sum(user_input.user_input_line_ids.mapped('percentage')) > 0:
                for line in user_input.user_input_line_ids:
                    quizz_score += (line.quizz_mark * line.percentage / 100)
                user_input.quizz_score = quizz_score
            else:
                super()._compute_quizz_score()

    def write(self, vals):
        res = super().write(vals)
        self.mapped('education_record_id')._onchange_survey_mark()
        return res


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input_line"

    percentage = fields.Float('Eval. percentage')
    labels_ids = fields.One2many(string='Types of answers', related="question_id.labels_ids")
    labels_ids_2 = fields.One2many(string='Types of answers', related="question_id.labels_ids_2")
    record_state = fields.Selection(
        'Education Record Status', related='user_input_id.state')
    competence_types = fields.Many2many(
        comodel_name='education.competence.type', string='Competence types',
        compute='compute_competence_types')

    def compute_competence_types(self):
        for record in self:
            record.competence_types = record.value_suggested_row.competence_types.filtered(
                lambda c: record.user_input_id.partner_id.current_level_id.id in c.education_level_ids.ids)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._compute_percentage()
        return res

    def _compute_percentage(self):
        for record in self:
            record.percentage = record.value_suggested_row.percentage

    def save_lines(self, user_input_id, question, post, answer_tag):
        res = super(SurveyUserInputLine, self).save_lines(user_input_id, question, post, answer_tag)
        user_input = self.env['survey.user_input'].browse(user_input_id)
        user_input.compute_average_grade()
        return res

    @api.depends('value_suggested')
    def onchange_value_suggested(self):
        self.ensure_one()
        self.quizz_mark = self.value_suggested.quizz_mark
        self.user_input_id.compute_average_grade()


class SurveyQuestionText(models.Model):
    _name = "survey.question.text"
    _description = 'Survey Question Text (Matrix)'

    responsible = fields.Many2one('hr.employee', string='Responsible Teacher', related="question_id.responsible")

    question_id = fields.Many2one(
        comodel_name="survey.question",
        string="Question",
        required=True,)

    label_id_1 = fields.Many2one(
        string="Survey Label 1",
        comodel_name="survey.label",
        required=True)

    label_id_2 = fields.Many2one(
        string="Survey Label 2",
        comodel_name="survey.label",
        required=True)

    text = fields.Text('Text')


class SurveyLabel(models.Model):
    _inherit = "survey.label"

    percentage = fields.Float('Eval. percentage')

    competence_types = fields.Many2many(
        comodel_name='education.competence.type', string='Competence types',
        relation='rel_competence_type_survey',
        column1='label_id', column2='competence_type_id')

    level_ids = fields.Many2many(
        comodel_name='education.level',
        related="question_id_2.level_ids")

    responsible = fields.Many2one(
        'hr.employee', string='Responsible Teacher',
        compute="_compute_label_responsible", store=True)

    color = fields.Text('Color Hex')

    def _compute_label_responsible(self):
        for record in self:
            record.responsible = record.question_id_2.responsible.id if record.question_id_2 else record.question_id.responsible.id

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._compute_label_responsible()
        return res


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    responsible = fields.Many2one('hr.employee', string='Responsible Teacher', related="survey_id.responsible")

#    labels_ids_2 = fields.One2many(copy=True)

    level_ids = fields.Many2many(
        comodel_name='education.level',
        related="page_id.level_ids")

    survey_text_ids = fields.One2many(
        string='Matrix Texts',
        comodel_name='survey.question.text',
        inverse_name='question_id',
      #  copy=True
    )

    @api.onchange('labels_ids_2', 'labels_ids_2.percentage')
    def _onchange_label_percentage(self):
        if sum(self.labels_ids_2.mapped('percentage')) > 100:
            raise UserError(
                _('The sum of all label percentages cannot be greater than 100.')
            )

    def create_survey_texts(self):
        for record in self:
            text_obj = self.env['survey.question.text']
            if record.type == 'matrix':
                for label in record.labels_ids:
                    for label2 in record.labels_ids_2:
                        text_obj.create({
                            'question_id': record.id,
                            'label_id_1': label.id,
                            'label_id_2': label2.id,
                        })
