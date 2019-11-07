# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class EducationNotebookLine(models.Model):
    _name = 'education.notebook.line'
    _description = 'Education notebook line'

    planification_id = fields.Many2one(comodel_name='education.schedule',
                                       string='Planification', required=True)
    teacher_id = fields.Many2one(related='planification_id.teacher_id',
                                 comodel_name='hr.employee', string='Teacher',
                                 store=True)
    a_year_id = fields.Many2one(related='planification_id.academic_year_id',
                                comodel_name='education.academic_year',
                                string='Academic year', store=True)
    education_center_id = fields.Many2one(related='planification_id.center_id',
                                          comodel_name='res.partner',
                                          string='Education center',
                                          store=True)
    classroom_id = fields.Many2one(related='planification_id.classroom_id',
                                   comodel_name='education.classroom',
                                   string='Classroom', store=True)
    task_type_id = fields.Many2one(related='planification_id.task_type_id',
                                   comodel_name='education.task_type',
                                   string='Task type', store=True)
    competence_id = fields.Many2one(comodel_name='education.competence',
                                    string='Competence', required=True)
    description = fields.Char(string='Description', required=True)
    eval_percent = fields.Integer(string='Evaluation percent (%)')
    eval_type = fields.Selection(selection=[
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
        ('final', 'Final')],
        string='Evaluation season', default='final', required=True
    )
    exam_ids = fields.One2many(comodel_name='education.exam',
                               inverse_name='n_line_id', string='Exams',
                               editable=True)
    num_exams = fields.Integer(compute='_compute_num_exams',
                               string='Number of exams')
    competence_type_id = fields.Many2one(comodel_name='education.competence.type',
                                         string='Competence type')
    father_competence_id = fields.Many2one(comodel_name='education.notebook.line',
                                           string='Father competence (notebobok line)',
                                           store=True)
    exists_master = fields.Boolean(string='Is master', compute='_compute_master_competences',
                                   default=False)
    notebook_line_child_ids = fields.One2many(comodel_name='education.notebook.line',
                                              inverse_name='father_competence_id',
                                              string='Son competences (notebook lines)',
                                              editable=True,
                                              store=True)
    comp_eval_check = fields.Boolean(string="Evaluation check for the competence",
                                     related='competence_id.evaluation_check',
                                     comodel_name='education.competence',
                                     default=False,
                                     store=True)
    comp_global_check = fields.Boolean(string="Global check for the competence",
                                       related='competence_id.global_check',
                                       comodel_name='education.competence',
                                       default=False,
                                       store=True)
    academic_record_ids = fields.One2many(comodel_name='education.record',
                                          inverse_name='n_line_id',
                                          string='Academic records',
                                          editable=True,
                                          store=True)
    father_father_competence_id = fields.Many2one(comodel_name='education.notebook.line',
                                                  string='Fathers father competence',
                                                  related='father_competence_id.father_competence_id',
                                                  store=True)
    all_exams_academic_records_count = fields.Integer(compute='_compute_all_exams_academic_records_count',
                                                      string='Academic records of all exams of the competence')
    evaluation_academic_records_count = fields.Integer(compute='_compute_evaluation_academic_records_count',
                                                       string='Evaluation records of notebook line')
    line_academic_records_count = fields.Integer(compute='_compute_line_academic_records_count',
                                                 string='Academic records of notebook line')

    # MUESTRA LOS REGISTROS ACADEMICOS ASOCIADOS A TODOS LOS EXAMENES DE LA COMPETENCIA+ LOS DE LA LINEA
    @api.multi
    def button_show_all_exams_academic_records(self):
        academic_record_lines = self.env['education.record']
        exam_ids = self.env['education.exam'].search([
            ('n_line_id', '=', self.id)])
        for exam in exam_ids:
            academic_record_lines = academic_record_lines + exam.academic_record_ids
        academic_record_lines = academic_record_lines + self.env['education.record'].search([
            ('n_line_id', '=', self.id)])

        context = dict(self.env.context or {})
        context['search_default_groupby_father_competence'] = True

        description = (self.planification_id.subject_id.description or
                       self.planification_id.task_type_id.description)
        return {
            'name': _('Academic records for all exams of {} [{}]').format(
                description, self.planification_id.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.record',
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('id', 'in', academic_record_lines.ids)],
        }

    # MUESTRA LOS REGISTROS ACADEMICOS ASOCIADOS A TODOS LOS EXAMENES DE LA COMPETENCIA+ LOS DE LA LINEA
    @api.multi
    def button_show_evaluation_academic_records(self):
        academic_record_lines = self.env['education.record']
        for eval_childs in self.notebook_line_child_ids:
            academic_record_lines = academic_record_lines + self.env['education.record'].search([
                ('n_line_id', '=', eval_childs.id)])
        academic_record_lines = academic_record_lines + self.env['education.record'].search([
            ('n_line_id', '=', self.id)])

        context = dict(self.env.context or {})
        context['search_default_groupby_father_competence'] = True

        description = (self.planification_id.subject_id.description or
                       self.planification_id.task_type_id.description)
        return {
            'name': _('Academic records for evaluations of {} [{}]').format(
                description, self.planification_id.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.record',
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('id', 'in', academic_record_lines.ids)],
        }

    # MUESTRA LOS REGISTROS ACADEMICOS DE TODOS LOS EXAMENES DE LA LINEA
    @api.multi
    def button_show_line_academic_records(self):
        academic_record_lines = self.env['education.record']
        academic_record_lines = academic_record_lines + self.env['education.record'].search([
            ('n_line_id', '=', self.id)])

        description = (self.planification_id.subject_id.description or
                       self.planification_id.task_type_id.description)
        return {
            'name': _('Academic records for {} [{}]').format(
                description, self.planification_id.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.record',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', academic_record_lines.ids)],
        }

    # CUENTA LOS REGISTROS ACADEMICOS ASOCIADOS A TODOS LOS EXAMENES DE LA COMPETENCIA + LOS DE LA LINEA
    @api.multi
    def _compute_all_exams_academic_records_count(self):
        for line in self:
            count = 0
            exam_ids = line.env['education.exam'].search([
                ('n_line_id', '=', line.id)])
            for exam in exam_ids:
                count = count + exam.academic_record_lines_count
            count = count + line.env['education.record'].search_count([
                ('n_line_id', '=', line.id)])
            line.all_exams_academic_records_count = count

    # CUENTA LOS REGISTROS ACADEMICOS ASOCIADOS A LAS EVALUACIONES DE LA COMPETENCIA + LOS DE LA LINEA
    @api.depends('notebook_line_child_ids')
    @api.multi
    def _compute_evaluation_academic_records_count(self):
        for line in self:
            count = 0
            for eval_childs in line.notebook_line_child_ids:
                count = count + line.env['education.record'].search_count([
                    ('n_line_id', '=', eval_childs.id)])
            count = count + line.env['education.record'].search_count([
                ('n_line_id', '=', line.id)])
            line.evaluation_academic_records_count = count

    # CUENTA LOS REGISTROS ACADEMICOS ASOCIADOS A LOS EXAMENES DE LA LINEA
    @api.multi
    def _compute_line_academic_records_count(self):
        for line in self:
            count = 0
            count = count + line.env['education.record'].search_count([
                ('n_line_id', '=', line.id)])
            line.line_academic_records_count = count

    # DEVUELVE TRUE SI LA LINEA CUADERNO TIENE UNA COMPETENCIA MASTER (TANTO LA COMPETENCIA COMO LA PADRE)
    @api.depends('competence_id')
    @api.multi
    def _compute_master_competences(self):
        for line in self:
            line.exists_master = line.competence_id.evaluation_check or line.competence_id.global_check or False

    @api.depends('exam_ids')
    @api.multi
    def _compute_num_exams(self):
        for record in self:
            record.num_exams = len(record.exam_ids)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Notebook line] for "{}" in "{}" with "{}" exams'.format(
                record.teacher_id.name, record.competence_id.name, record.num_exams)))
        return result
