# Copyright (c) 2019 Adrian Revilla <adrianrevilla@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, exceptions


class educationExpedient(models.Model):
    _name = 'education.expedient'
    _description = 'Educational expedient'

    exam_id = fields.Many2one(comodel_name='education.notebook.line',
                              string='Exams for notebook line', required=True)
    date = fields.Date(related='exam_id.exam_ids.date', store=True,
                       string='Date')
    subject_id = fields.Many2one(related='exam_id.planification_id.subject_id',
                                 store=True, string='Subject')
    teacher_id = fields.Many2one(related='exam_id.planification_id.teacher_id',
                                 store=True, string='Teacher')
    kid_id = fields.Many2one(comodel_name='res.partner', string='Kid',
                             required=True)
    numeric_mark = fields.Float(string='Numeric mark')
    mark_code = fields.Char(compute='_compute_numeric_mark',
                            string='Numeric mark code', store=True)
    behaviour_mark = fields.Many2one(comodel_name='education.mark.behaviour',
                                     string='Behaviour mark')

    @api.multi
    @api.depends('numeric_mark')
    def _compute_numeric_mark(self):
        for record in self:
            if record.numeric_mark >= 0.0 and record.numeric_mark <= 2.5:
                record.mark_code = 'Very bad'
            elif record.numeric_mark > 2.5 and record.numeric_mark < 4:
                record.mark_code = 'Bad'
            elif record.numeric_mark >= 4 and record.numeric_mark < 6:
                record.mark_code = 'Normal'
            elif record.numeric_mark >= 6 and record.numeric_mark < 8:
                record.mark_code = 'Good'
            elif record.numeric_mark >= 8 and record.numeric_mark <= 10:
                record.mark_code = 'Very good'

    @api.constrains('numeric_mark')
    def _check_mark(self):
        if self.numeric_mark < 0.0 or self.numeric_mark > 10.0:
            raise exceptions.ValidationError('Mark value has to be between 0 and 10.')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Expedient line] Teacher: {} Kid: {}'.format(
                record.teacher_id.name, record.kid_id.name)))
        return result