# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationNumericMark(models.Model):
    _name = 'education.mark.numeric'
    _description = 'Numeric mark'

    name = fields.Char(string='Name', required=True)
    reduced_name = fields.Char(string='Reduced name')
    initial_mark = fields.Float(string='Initial mark', required=True)
    final_mark = fields.Float(string='Final mark', required=True)


class EducationBehaviourMark(models.Model):
    _name = 'education.mark.behaviour'
    _description = 'Behaviour mark'

    name = fields.Char(string='Name')
    code = fields.Selection(selection=[
        ('A', 'Very good'),
        ('B', 'Good'),
        ('C', 'Normal'),
        ('D', 'Insuficient'),
        ('E', 'Bad'),
        ('F', 'Very bad')],
        string='Code', default='C', required=True
    )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Behaviour mark] {} {}'.format(
                record.code, record.name)))
        return result


class EducationExamType(models.Model):
    _name = 'education.exam.type'
    _description = 'Exam type'

    name = fields.Char(string='Exam types name')
    e_type = fields.Selection(selection=[
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


class EducationCompetenceType(models.Model):
    _name = 'education.competence.type'
    _description = 'Competence type'

    name = fields.Char(string='Competence type name')
