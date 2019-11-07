# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date


class EducationExam(models.Model):
    _name = 'education.exam'
    _description = 'Education exam'

    name = fields.Char(string='Exam name', required=True)
    exam_type_id = fields.Many2one(comodel_name='education.exam.type',
                                   string='Exam type', required=True)
    n_line_id = fields.Many2one(comodel_name='education.notebook.line',
                                string='Exam asociated competence',
                                required=True)
    eval_type = fields.Selection(related='n_line_id.eval_type',
                                 string='Evaluation season')
    date = fields.Date(string='Exam date')
    eval_percent = fields.Float(string='Percent (%)', required=True)
    state = fields.Selection(selection=[
                            ('notgenerated', 'Not done'),
                            ('revision in course', 'Revised'),
                            ('generated', 'Revised and generated'),
                            ('closed', 'Closed'), ],
                            default='notgenerated')
    academic_record_lines_count = fields.Integer(compute='_compute_academic_record_lines_count',
                                                 string='Academic record lines')
    recovery_exam_to_id = fields.Many2one(comodel_name='education.exam',
                                          string='Recupera a')
    type_exam_name = fields.Selection(related='exam_type_id.e_type',
                                      string='Tipo de examen (nombre)')
    mark_close_date = fields.Date(string='Date for closing exam')
    academic_record_ids = fields.One2many(comodel_name='education.record',
                                          inverse_name='exam_id',
                                          string='Academic records',
                                          editable=True)
    description = fields.Char(string='Exam description')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if not record.recovery_exam_to_id:
                result.append((record.id, '{} [{}]'.format(
                    record.name, record.exam_type_id.e_type)))
            else:
                result.append((record.id, '{} [{}] , recupera a: {} [{}]'.format(
                                record.name,
                                record.exam_type_id.e_type,
                                record.recovery_exam_to_id.name,
                                record.recovery_exam_to_id.exam_type_id.e_type)))
        return result

    @api.multi
    def action_generate_record(self):
        for exam in self:
            if exam.academic_record_lines_count == 0:
                academic_record_line = exam.env['education.record']
                for kid in exam.n_line_id.planification_id.student_ids:
                    academic_record_line_data = {'exam_id': exam.id,
                                                 'date': exam.date,
                                                 'kid_id': kid.id,
                                                 'n_line_id': exam.n_line_id.id,
                                                 }
                    academic_record_line.create(academic_record_line_data)
                    exam.state = 'generated'

    @api.multi
    @api.depends('academic_record_ids')
    def _compute_academic_record_lines_count(self):
        for exam in self:
            exam.academic_record_lines_count = len(exam.academic_record_ids)

    @api.multi
    def button_show_academic_record_lines(self):
        record_obj = self.env['education.record'].search([
            ('exam_id', '=', self.id)])
        my_context = self.env.context.copy()
        my_context['default_exam_id'] = self.id
        my_context['search_default_exam_id'] = self.id
        return {
            'name': _('Academic record'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.record',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', record_obj.ids)],
        }

    @api.multi
    def action_close_exam(self):
        for exam in self:
            exam.state = 'closed'
            if not exam.mark_close_date:
                exam.mark_close_date = date.today()

    @api.multi
    def action_revise_exam(self):
        for exam in self:
            exam.state = 'revision in course'
