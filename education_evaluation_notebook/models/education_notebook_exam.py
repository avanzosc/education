# Copyright (c) 2019 Adrian Revilla <adrianrevilla@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, exceptions


class educationExam(models.Model):
    _name = 'education.exam'
    _description = 'Educational exams'
    
    name = fields.Char(string='Exam name', required=True)
    exam_type = fields.Many2one(comodel_name='education.exam.type',
                                string='Exam type', required=True)
    n_line = fields.Many2one(comodel_name='education.notebook.line', 
                             string='Exam asociated competence',
                             ondelete='cascade')
    eval_type = fields.Selection(related='n_line.eval_type',
                                 string='Evaluation season')
    date = fields.Date(string='Exam date',required=True)
    eval_percent = fields.Integer(string='Percent (%)',required=True)
    messages_ok = fields.Char()
    messages_error = fields.Char()
    state = fields.Selection([
            ('notgenerated', 'Expedient not generated'),
            ('generated', 'Expedient generated'),
            ],default='notgenerated')

    @api.constrains('eval_percent')
    def _check_eval_percent(self):
        for exam in self:
            exam.clear_messages()
            if exam.eval_percent < 0 or exam.eval_percent > 100:
                raise exceptions.ValidationError('Percent incorrect format')

    @api.multi
    def name_get(self):
        for exam in self:
            exam.clear_messages()
            result = []
            for record in exam:
                result.append((record.id, '[Exam] {}'.format(
                    record.exam_type.name)))
            return result

    @api.multi
    def action_generate_expedient(self):
        for exam in self:
            exam.clear_messages()
            exam_id = exam.env['education.exam'].search([('id', '=', exam.id)])
            if exam_id:
                #kid_ids = exam.env['res.partner'].search([('id', '=', exam.n_line.planification_id.student_ids.id)])
                kid_ids = exam.n_line.planification_id.student_ids
                if kid_ids:
                    write_line = exam.env['education.expedient']
                    for record in kid_ids:
                        line_data = {
                        'id':exam.id,
                        'exam_id': exam_id.n_line.id,
                        'date': exam_id.date,
                        'subject_id':exam_id.n_line.planification_id.subject_id.id,
                        'teacher_id': exam_id.n_line.planification_id.teacher_id.id,
                        'kid_id': record.id,
                        }
                        try:
                            write_line.create(line_data)
                        except Exception as error:
                            exam.messages_error = 'Error generating expedient lines!'
                            self.write({'state': 'notgenerated',})
                    self.messages_ok = 'Expedient lines generated successfully!'
                    self.write({'state': 'generated',})
                else:
                    if not exam.n_line:
                        exam.messages_error = 'No teachers notebook line asociated to the exam!'
                        self.write({'state': 'notgenerated',})
                    else:
                        exam.messages_error = 'Not kids for this exam to generate expedient!'
                        self.write({'state': 'notgenerated',})
            else:
                exam.messages_error = 'Is not any exam to generate lines!'
                self.write({'state': 'notgenerated',})

    @api.multi     
    def clear_messages(self):
        for exam in self:
            exam.messages_ok=''
            exam.messages_error=''