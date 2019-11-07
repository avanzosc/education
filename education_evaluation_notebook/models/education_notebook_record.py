# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class EducationRecord(models.Model):
    _name = 'education.record'
    _description = 'Academic record'

    exam_id = fields.Many2one(comodel_name='education.exam',
                              string='Exam')
    exam_type = fields.Selection(related='exam_id.exam_type_id.e_type',
                                 comodel_name='education.exam.type',
                                 store=True, string='Exam type')
    exam_eval_percent = fields.Float(compute='_compute_eval_percent',
                                     string='Evaluation percent')
    date = fields.Date(related='exam_id.date', store=True,
                       string='Date')
    subject_id = fields.Many2one(related='n_line_id.planification_id.subject_id',
                                 comodel_name='education.subject',
                                 store=True, string='Subject')
    teacher_id = fields.Many2one(related='n_line_id.planification_id.teacher_id',
                                 comodel_name='hr.employee',
                                 store=True, string='Teacher')
    kid_id = fields.Many2one(comodel_name='res.partner', string='Kid',
                             required=True)
    numeric_mark = fields.Float(string='Numeric mark', store=True)
    competence = fields.Many2one(related='n_line_id.competence_id',
                                 comodel_name='education.competence',
                                 store=True, string='Competence')
    competence_father = fields.Many2one(related='n_line_id.father_competence_id.competence_id',
                                        comodel_name='education.competence',
                                        store=True, string='Father competence')
    competence_father_father = fields.Many2one(related='n_line_id.father_competence_id.father_competence_id.competence_id',
                                               comodel_name='education.competence',
                                               store=True, string='Fathers father competence')
    behaviour_mark_id = fields.Many2one(comodel_name='education.mark.behaviour',
                                        string='Behaviour mark')
    master_competence_eval_check = fields.Boolean(string="Evaluation check for the competence",
                                                  related='n_line_id.competence_id.evaluation_check',
                                                  default=False)
    master_competence_global_check = fields.Boolean(string="Global check for the competence",
                                                    related='n_line_id.competence_id.global_check',
                                                    default=False)
    calculated_numeric_mark = fields.Float(compute='_compute_generate_marks',
                                           string='Calculated numeric mark',
                                           store=True)
    n_mark = fields.Many2one(comodel_name='education.mark.numeric',
                             string='Numeric mark', store=True)
    n_mark_name = fields.Char(related='n_mark.name',
                              comodel_name='education.mark.numeric',
                              string='Numeric mark name',
                              store=True)
    n_mark_reduced_name = fields.Char(related='n_mark.reduced_name',
                                      comodel_name='education.mark.numeric',
                                      string='Reduced numeric mark name',
                                      store=True)
    father_record_id = fields.Many2one(comodel_name='education.record',
                                       string='Father record', store=True)
    father_father_record_id = fields.Many2one(related= 'father_record_id.father_record_id',
                                       comodel_name='education.record',
                                       string='Father record', store=True)
    child_record_ids = fields.One2many(comodel_name='education.record',
                                       inverse_name='father_record_id',
                                       string='Academic records sons',
                                       editable=True)
    n_line_id = fields.Many2one(comodel_name='education.notebook.line',
                                store=True, string='Notebook line')
    child_academic_records_count = fields.Integer(compute='_compute_count_record_childs',
                                                  string='Child records')
    competence_type_check = fields.Char(string="Check for the competence",
                                        compute='_compute_competence_check',
                                        store=True)

    @api.multi
    @api.depends('master_competence_global_check', 'master_competence_eval_check')
    def _compute_competence_check(self):
        for record in self:
            if record.master_competence_global_check:
                record.type_check = "Global"
            elif record.master_competence_eval_check:
                record.type_check = "Eval"
            else:
                record.type_check = "Normal"

    # CUENTA LOS REGISTROS ACADEMICOS HIJOS
    @api.multi
    @api.depends('child_record_ids')
    def _compute_count_record_childs(self):
        for record in self:
            record.child_academic_records_count = len(record.child_record_ids)

    # MUESTRA LOS REGISTROS ACADEMICOS HIJOS
    @api.multi
    def button_show_child_academic_records(self):
        my_context = self.env.context.copy()
        my_context['default_childs_for_academic_records_id'] = self.id
        my_context['search_default_childs_for_academic_records_id'] = self.id

        return {
            'name': _('Academic record childs for {} [{}]').format(
                self.exam_id.name, self.kid_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.record',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', self.child_record_ids.ids)],
        }

    # MUESTRA EL PORCENTAJE CORRESPONDIENTE
    @api.multi
    @api.depends('exam_id', 'exam_id.eval_percent',
                 'n_line_id', 'n_line_id.eval_percent')
    def _compute_eval_percent(self):
        for record in self:
            if record.exam_id:
                record.exam_eval_percent = record.exam_id.eval_percent
            else:
                record.exam_eval_percent = record.n_line_id.eval_percent
            # record.exam_eval_percent = record.exam_id.eval_percent if record.exam_id else record.n_line_id.eval_percent

    # MUESTRA EL CODIGO DE LA NOTA NUMERICA
    @api.multi
    @api.onchange('numeric_mark')
    def _compute_mark_code(self):
        for record in self:
            mark_obj = record.env['education.mark.numeric'].search([
                ('initial_mark', '<=', record.numeric_mark),
                ('final_mark', '>=', record.numeric_mark)], limit=1)
            record.n_mark = mark_obj

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[Academic record line] Teacher: {} Kid: {}'.format(
                record.teacher_id.name, record.kid_id.name)))
        return result

    # COMPRUEBA SI UN EXAMEN DE UN ACADEMIC RECORD ES DE RECUPERACION
    def check_recuperation_exam_for_record(self, record):
        exam_obj = self.env['education.exam'].search([
            ('recovery_exam_to_id', '=', record.exam_id.id),
            ('exam_type_id.e_type', '=', 'recuperation exam')], limit=1)
        return exam_obj

    @api.multi
    @api.depends('child_record_ids','child_record_ids.numeric_mark', 'child_record_ids.exam_eval_percent')
    def _compute_generate_marks(self):
        for record in self:
            suma = 0
            for child in record.child_record_ids:
                examen_recuperacion = record.check_recuperation_exam_for_record(record)
                if len(examen_recuperacion) == 0:
                    child.calculated_numeric_mark = child.numeric_mark * (child.exam_eval_percent/100)
                else:
                    recuperation_exam_record = record.env['education.record'].search([('exam_id', '=', examen_recuperacion.id)], limit=1)
                    recuperation_exam_record.calculated_numeric_mark = recuperation_exam_record.numeric_mark * (recuperation_exam_record.exam_eval_percent/100)
                suma += child.calculated_numeric_mark
            record.calculated_numeric_mark = suma
