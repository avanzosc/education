# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EducationHomework(models.Model):
    _name = 'education.homework'
    _description = 'Education homework'

    description = fields.Char(string="Description", required=True)
    date = fields.Date(string='Date', required=True)
    planification_id = fields.Many2one(comodel_name='education.schedule',
                                       string='Planification')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            description = (record.planification_id.subject_id.description or
                           record.planification_id.task_type_id.description)
            result.append((record.id, 'Homework "{}" for "{}"'.format(
                record.description, description)))
        return result

    @api.depends('description')
    @api.one
    def check_duplicated_homework_competence(self):
        competence_ids = self.env['education.competence'].search([
            ('name', '=', 'Generated competence for homework '+str(
                self.description))])
        return len(competence_ids)

    @api.depends('date')
    @api.one
    def check_data_for_evaluation_season(self):
        date_month = str(self.date).split('-')[1]
        date_day = str(self.date).split('-')[2]
        if int(date_month) >= 9 and int(date_month) <= 1:
            if int(date_month) == 1 and int(date_day) > 15:
                return 'second'
            return 'first'
        elif int(date_month) > 1 and int(date_month) <= 4:
            if int(date_month) == 4 and int(date_day) > 15:
                return 'third'
            return 'second'
        else:
            return 'third'

    @api.depends('description', 'planification_id')
    @api.one
    def action_generate_homework_competence(self):
        duplicated = self.check_duplicated_homework_competence()
        if duplicated[0] == 0:
            eval_season = self.check_data_for_evaluation_season()
            competence_line = self.env['education.competence']
            notebook_line = self.env['education.notebook.line']
            exam_type_line = self.env['education.exam.type']
            exam_line = self.env['education.exam']
            competence_line_data = {
                'name': 'Generated competence for homework '+str(
                    self.description),
                'eval_mode': 'numeric',
                }
            comp_obj = competence_line.create(competence_line_data)
            notebook_line_data = {
                'planification_id': self.planification_id.id,
                'description': 'Generated description for homework '+str(
                    self.description),
                'eval_type': eval_season[0],
                'competence_id': comp_obj.id,
                }
            line_obj = notebook_line.create(notebook_line_data)
            exam_type_data_line = {
                'name': 'Generated exam type for homework '+str(
                    self.description),
                'e_type': 'control exam',
                }
            e_type_obj = exam_type_line.create(exam_type_data_line)
            exam_data_line = {
                'name': 'Generated exam for homework '+str(self.description),
                'exam_type_id': e_type_obj.id,
                'n_line_id': line_obj.id,
                'eval_percent': 0,
                }
            exam_line.create(exam_data_line)
