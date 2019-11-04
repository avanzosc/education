# Copyright (c) 2019 Adrian Revilla <adrianrevilla@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, api


class educationNotebookLine(models.Model):
    _name = 'education.notebook.line'
    _description = 'Education notebook different lines'
    
    planification_id = fields.Many2one(comodel_name='education.schedule',
                                       string='Planification', required=True)
    teacher = fields.Char(related='planification_id.teacher_id.name',
                          string='Teacher', store=True)
    a_year = fields.Char(related='planification_id.academic_year_id.name',
                         string='Academic year', store=True)
    education_center = fields.Char(related='planification_id.center_id.name',
                                   string='Education center', store=True)
    classroom = fields.Char(related='planification_id.classroom_id.education_code',
                            string='Classrom', store=True)
    task_type = fields.Selection(related='planification_id.task_type_type',
                                 string='Task type', store=True)
    competence = fields.Many2one(comodel_name='education.competence',
                                 string='Competence', required=True)
    description = fields.Char(string='Description', required=True)
    eval_percent = fields.Integer(string='Evaluation percent (%)')
    mark_exam = fields.Char(string='Formula nota del examen')
    eval_type = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
        ('final', 'Final')],
        string='Evaluation season', default='final', required=True
    )
    exam_ids = fields.One2many(comodel_name='education.exam',
                               inverse_name='n_line', string='Exams')
    num_exams = fields.Integer(compute='_compute_num_exams',
                               string='Number of exams')

    @api.constrains('eval_percent')
    def _check_eval_percent(self):
        if self.eval_percent < 0 or self.eval_percent > 100:
            raise exceptions.ValidationError('Percent has incorrect format')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Notebook line] for "{}" in "{}" with "{}" exams'.format(
                record.teacher,record.competence.name, record.num_exams)))
        return result

    @api.depends('exam_ids')
    def _compute_num_exams(self):
        for record in self:
            if not record.exam_ids:
                record.num_exams = 0
            else:
                record.num_exams = len(record.exam_ids)