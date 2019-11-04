# Copyright (c) 2019 Adrian Revilla <adrianrevilla@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, api

class educationNumericMark(models.Model):
    _name = 'education.mark.numeric'
    _description = 'Numeric mark'

    name = fields.Char(string='Name', required=True)
    reduced_name = fields.Char(string='Reduced name')
    initial_mark = fields.Float(string='Initial mark', required=True)
    final_mark = fields.Float(string='Final mark', required=True)
    
    @api.constrains('initial_mark','final_mark')
    def _check_mark(self):
        if self.initial_mark < 0.0 or self.initial_mark > 10.0:
            raise exceptions.ValidationError('Initial marks value has to be between 0 and 10.')
        if self.final_mark < 0.0 or self.final_mark > 10.0:
            raise exceptions.ValidationError('Final marks value has to be between 0 and 10.')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Numeric mark] Initial mark: {}, Final mark: {}'.format(
                record.initial_mark, record.final_mark)))
        return result

class educationBehaviourMark(models.Model):
    _name = 'education.mark.behaviour'
    _description = 'Behaviour mark'
    
    name = fields.Selection([
        ('very good', 'Very good'),
        ('good', 'Good'),
        ('normal', 'Normal'),
        ('bad', 'Bad')],
        string='Name', default='normal', required=True
    )
    code = fields.Selection([
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D')],
        string='Code', default='c', required=True
    )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Behaviour mark] {}'.format(
                record.code, record.name)))
        return result

class educationExamType(models.Model):
    _name = 'education.exam.type'
    _description = 'Exam type'
    
    name = fields.Char(string='Exam types name')
    e_type = fields.Selection([
        ('control exam', 'Control exam'),
        ('evaluation exam', 'Evaluation exam'),
        ('global exam', 'Global exam'),
        ('project', 'Project'),
        ('recuperation exam', 'Recuperation exam')],
        string='Exam type', default='control exam', required=True
    )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Exam type] {}'.format(
                record.e_type)))
        return result