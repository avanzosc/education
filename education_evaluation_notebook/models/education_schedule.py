# Copyright 2019 Adrian Revilla - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class EducationSchedule(models.Model):
    _inherit = 'education.schedule'

    notebook_lines_count = fields.Integer(compute='_compute_notebook_lines_count',
                                          string='Teacher notebook lines')
    master_competences_count = fields.Integer(compute='_compute_master_competences_count',
                                              string='Master competences')
    notebook_exams_count = fields.Integer(compute='_compute_notebook_exams_count',
                                          string='Notebook related exams')
    exams_academic_record_count = fields.Integer(compute='_compute_exams_academic_records_count',
                                                 string='Academic records of exams')
    son_competences_count = fields.Integer(compute='_compute_son_competences_count',
                                           string='Son competences')
    homework_ids = fields.One2many(comodel_name='education.homework',
                                   inverse_name='planification_id',
                                   string='Homeworks')
    homeworks_count = fields.Integer(compute='_compute_homeworks_count',
                                     string='Homerwork count')
########################################### FUNCIONES COMPUTE ###############################################
    # CUENTA EL NUMERO DE DEBERES DE LA PLANIFICACION
    @api.multi
    def _compute_homeworks_count(self):
        for schedule in self:
            schedule.homeworks_count = self.env['education.homework'].search_count([
                ('planification_id', '=', schedule.id)])

    # CUENTA EL NUMERO DE LINEAS DE CUADERNO ASOCIADAS A LA PLANIFICACIÓN
    @api.multi
    def _compute_notebook_lines_count(self):
        for schedule in self:
            schedule.notebook_lines_count = self.env['education.notebook.line'].search_count([
                ('planification_id', '=', schedule.id)])

    # CUENTA EL NUMERO DE EXAMENES PARA LAS LINEAS DE CUADERNO DE LA PLANIFICACION
    @api.multi
    def _compute_notebook_exams_count(self):
        count = 0
        notebook_lines = self.env['education.notebook.line'].search([(
            'planification_id', '=', self.id)])
        for line in notebook_lines:
            count = count + len(line.exam_ids)
        self.notebook_exams_count = count

    # CUENTA LOS REGISTROS ACADEMICOS DE LOS EXAMENES DE LAS LINES DE CUADERNO DE LA PLANIFICACION
    @api.multi
    def _compute_exams_academic_records_count(self):
        count = 0
        notebook_lines = self.env['education.notebook.line'].search([(
            'planification_id', '=', self.id)])
        for line in notebook_lines:
            count = count + self.env['education.record'].search_count([
                ('n_line_id', '=', line.id)])
        self.exams_academic_record_count = count

    # CUENTA EL NUMERO DE COMPETENCIAS MASTER ASOCIADAS A LA PLANIFICACION
    @api.multi
    def _compute_master_competences_count(self):
        count = 0
        notebook_line_obj = self.env['education.notebook.line'].search([
            ('planification_id', '=', self.id)])
        for line in notebook_line_obj:
            if (line.competence_id.evaluation_check or line.competence_id.global_check):
                count = count + 1
        self.master_competences_count = count

    # CUENTA EL NUMERO DE COMPETENCIAS NORMALES ASOCIADAS A LA PLANIFICACION
    @api.multi
    def _compute_son_competences_count(self):
        count_son = 0
        notebook_line_obj = self.env['education.notebook.line'].search([
            ('planification_id', '=', self.id)])
        for line in notebook_line_obj:
            if not (line.competence_id.evaluation_check or line.competence_id.global_check):
                count_son = count_son + 1
        self.son_competences_count = count_son

################################################VISTAS FILTRADAS#######################################################
    # MUESTRA LOS REGISTROS DEBERES DE LA PLANIFICACION
    @api.multi
    def button_show_homeworks(self):
        homework_lines = self.env['education.homework'].search([(
            'planification_id', '=', self.id)])
        my_context = self.env.context.copy()
        my_context['default_planification_for_homeworks_id'] = self.id
        my_context['search_default_planification_for_homeworks_id'] = self.id
        description = (self.subject_id.description or
                       self.task_type_id.description)
        return {
            'name': _('Homeworks for {} [{}]').format(
                description, self.teacher_id.name),
            'view_type': 'calendar',
            'view_mode': 'calendar',
            'res_model': 'education.homework',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', homework_lines.ids)],
        }

    # MUESTRA LOS REGISTROS ACADEMICOS DE LOS EXAMENES DE LAS LINEAS DE CUADERNO DE LA PLANIFICACION
    @api.multi
    def button_show_exams_academic_records(self):
        academic_record_lines = self.env['education.record']
        notebook_lines = self.env['education.notebook.line'].search([(
            'planification_id', '=', self.id)])
        for line in notebook_lines:
            academic_record_lines = academic_record_lines + self.env['education.record'].search([
                ('n_line_id', '=', line.id)])

        my_context = self.env.context.copy()
        my_context['default_planification_for_academic_records_id'] = self.id
        my_context['search_default_planification_for_academic_records_id'] = self.id
        description = (self.subject_id.description or
                       self.task_type_id.description)
        return {
            'name': _('Academic records for {} [{}]').format(
                description, self.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.record',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', academic_record_lines.ids)],
        }

    # MUESTRA LOS EXAMENES DE LAS LINEAS DE CUADERNO DE LA PLANIFICACION
    @api.multi
    def button_show_notebook_exams(self):
        exam_lines = self.env['education.exam']
        notebook_lines = self.env['education.notebook.line'].search([(
            'planification_id', '=', self.id)])
        for line in notebook_lines:
            exam_lines = exam_lines + line.exam_ids

        my_context = self.env.context.copy()
        my_context['default_planification_for_exams_id'] = self.id
        my_context['search_default_planification_for_exams_id'] = self.id
        description = (self.subject_id.description or
                       self.task_type_id.description)
        return {
            'name': _('Exams for {} [{}]').format(
                description, self.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.exam',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', exam_lines.ids)],
        }

    # MUESTRA LAS LINEAS DE CUADERNO DE LA PLANIFICACION
    @api.multi
    def button_show_notebook_lines(self):
        notebook_lines = self.env['education.notebook.line'].search([(
            'planification_id', '=', self.id)])
        my_context = self.env.context.copy()
        my_context['default_planification_id'] = self.id
        my_context['search_default_planification_id'] = self.id
        description = (self.subject_id.description or
                       self.task_type_id.description)
        return {
            'name': _('Notebook lines for {} [{}]').format(
                description, self.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.notebook.line',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', notebook_lines.ids)],
        }

    # MUESTRA LAS COMPETENCIAS MASTER DE ESA PLANIFICACION
    @api.multi
    def button_show_master_generated_competences(self):
        notebook_lines_master_competence_child = self.env['education.notebook.line'].search([
            '&',
            ('planification_id', '=', self.id),
            '|',
            ('competence_id.evaluation_check', '=', True),
            ('competence_id.global_check', '=', True)
            ])
        my_context = self.env.context.copy()
        my_context['default_planification_master_competences_id'] = self.id
        my_context['search_default_planification_master_competences_id'] = self.id
        description = (self.subject_id.description or
                       self.task_type_id.description)
        return {
            'name': _('Master competences for {} [{}]').format(
                description, self.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.notebook.line',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', notebook_lines_master_competence_child.ids)],
        }

    # MUESTRA LAS COMPETENCIAS NORMALES DE LA PLANIFICACIÓN
    @api.multi
    def button_show_son_generated_competences(self):
        notebook_lines_son_competence_child = self.env['education.notebook.line'].search([
            '&',
            ('planification_id', '=', self.id),
            '&',
            ('competence_id.evaluation_check', '!=', True),
            ('competence_id.global_check', '!=', True)
            ])
        my_context = self.env.context.copy()
        my_context['default_planification_son_competences_id'] = self.id
        my_context['search_default_planification_son_competences_id'] = self.id
        description = (self.subject_id.description or
                       self.task_type_id.description)
        return {
            'name': _('Son competences for {} [{}]').format(
                description, self.teacher_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.notebook.line',
            'type': 'ir.actions.act_window',
            'context': my_context,
            'domain': [('id', 'in', notebook_lines_son_competence_child.ids)],
        }

########################################COMPROBAR DUPLICADOS#########################################

    @api.multi
    def check_duplicate_global_competence(self):
        global_competence_line = self.env['education.competence'].search([
            ('global_check', '=', 'True'),
            ('name', '=', 'Master global competence generated')])
        if len(global_competence_line) == 1:
            return global_competence_line

    @api.multi
    def check_duplicate_eval_competence(self):
        eval_competence_line = self.env['education.competence'].search([
            ('evaluation_check', '=', 'True'),
            ('name', '=', 'Master evaluation competence generated')])
        if len(eval_competence_line) == 1:
            return eval_competence_line

    @api.multi
    def check_duplicate_son_competence(self):
        son_competence_line = self.env['education.competence'].search([
            ('evaluation_check', '!=', 'True'),
            ('global_check', '!=', 'True'),
            ('name', '=', 'Son competence generated')])
        if len(son_competence_line) == 1:
            return son_competence_line

    @api.multi
    def check_duplicate_numeric_marks(self):
        numeric_mark_line = self.env['education.mark.numeric'].search([
            ('reduced_name', 'in', ('VB', 'B', 'I', 'N', 'G', 'VG'))])
        if len(numeric_mark_line) == 6:
            return numeric_mark_line

    def check_duplicate_evaluations_for_courses_and_schools(self, course):
        evaluation_ids = self.env['education.academic_year.evaluation'].search([
            ('course_id', '=', course.id)])
        if len(evaluation_ids) == 3:
            for e in evaluation_ids:
                if not (e.name == 'First evaluation generated' or e.name == 'Second evaluation generated' or e.name == 'Third evaluation generated'):
                    return evaluation_ids

########################################GENERA EXAMTYPES+EVALUATIONS+MARKS#########################################
    # GENERA LA COMPETENCIA MASTER GLOBAL + LINEA DE CUADERNO PARA LA PLANIFICACION
    @api.multi
    def generate_numeric_marks(self):
        duplicated = self.check_duplicate_numeric_marks()
        if duplicated == None:
            numeric_mark_line = self.env['education.mark.numeric']
            vb_numeric_mark_line_data = {'name': 'Generated Very Bad',
                                         'reduced_name': 'VB',
                                         'initial_mark': 0.0,
                                         'final_mark': 1.99,
                                         }
            b_numeric_mark_line_data = {'name': 'Generated Bad',
                                        'reduced_name': 'B',
                                        'initial_mark': 2.0,
                                        'final_mark': 3.99,
                                        }
            i_numeric_mark_line_data = {'name': 'Generated Insuficient',
                                        'reduced_name': 'I',
                                        'initial_mark': 4.0,
                                        'final_mark': 4.99,
                                        }
            n_numeric_mark_line_data = {'name': 'Generated Normal',
                                        'reduced_name': 'N',
                                        'initial_mark': 5.0,
                                        'final_mark': 5.99,
                                        }
            g_numeric_mark_line_data = {'name': 'Generated Good',
                                        'reduced_name': 'G',
                                        'initial_mark': 6.0,
                                        'final_mark': 7.99,
                                        }
            vg_numeric_mark_line_data = {'name': 'Generated Very Good',
                                         'reduced_name': 'VG',
                                         'initial_mark': 8.0,
                                         'final_mark': 10.0,
                                         }
            numeric_mark_line.create(vb_numeric_mark_line_data)
            numeric_mark_line.create(b_numeric_mark_line_data)
            numeric_mark_line.create(i_numeric_mark_line_data)
            numeric_mark_line.create(n_numeric_mark_line_data)
            numeric_mark_line.create(g_numeric_mark_line_data)
            numeric_mark_line.create(vg_numeric_mark_line_data)

#############################################GENERA COMPETENCES+NOTEBOOKLINES#######################################
    # GENERA LA COMPETENCIA MASTER GLOBAL + LINEA DE CUADERNO PARA LA PLANIFICACION
    @api.multi
    def generate_global_competence(self):
        duplicated = self.check_duplicate_global_competence()
        if duplicated == None:
            master_global_competence_line = self.env['education.competence']
            master_global_competence_line_data = {'name': 'Master global competence generated',
                                                  'eval_mode': 'numeric',
                                                  'evaluation_check': False,
                                                  'global_check': True,
                                                  }
            master_global_competence_created = master_global_competence_line.create(master_global_competence_line_data)
        else:
            master_global_competence_created = duplicated

        notebook_line = self.env['education.notebook.line']
        notebook_line_data = {
            'planification_id': self.id,
            'description': 'Description for the master global competence in the notebook line',
            'eval_type': 'final',
            'competence_id': master_global_competence_created.id,
            'exists_master': True,
            'eval_percent': 100,
            }
        return notebook_line.create(notebook_line_data)

    # GENERA LAS COMPETENCIAS MASTER DE EVALUACION + LINEA DE CUADERNO
    @api.multi
    def generate_evaluation_competences(self, notebook_line_global_comp):
        duplicated = self.check_duplicate_eval_competence()
        if duplicated == None:
            master_eval_competence_line = self.env['education.competence']
            master_eval_competence_line_data = {'name': 'Master evaluation competence generated',
                                                'eval_mode': 'numeric',
                                                'evaluation_check': True,
                                                'global_check': False,
                                                }
            master_eval_competence_created = master_eval_competence_line.create(
                master_eval_competence_line_data)
        else:
            master_eval_competence_created = duplicated

        notebook_line = self.env['education.notebook.line']
        notebook_line_first_eval_data = {'planification_id': self.id,
                                         'description': 'Description for the master first evaluation competence in the notebook line',
                                         'eval_type': 'first',
                                         'competence_id': master_eval_competence_created.id,
                                         'father_competence_id': notebook_line_global_comp.id,
                                         'exists_master': True,
                                         'eval_percent': 33,
                                         }
        notebook_line_second_eval_data = {'planification_id': self.id,
                                          'description': 'Description for the master second evaluation competence in the notebook line',
                                          'eval_type': 'second',
                                          'competence_id': master_eval_competence_created.id,
                                          'father_competence_id': notebook_line_global_comp.id,
                                          'exists_master': True,
                                          'eval_percent': 33,
                                          }
        notebook_line_third_eval_data = {'planification_id': self.id,
                                         'description': 'Description for the master third evaluation competence in the notebook line',
                                         'eval_type': 'third',
                                         'competence_id': master_eval_competence_created.id,
                                         'father_competence_id': notebook_line_global_comp.id,
                                         'exists_master': True,
                                         'eval_percent': 33,
                                         }
        return notebook_line.create(
            notebook_line_first_eval_data), notebook_line.create(
                notebook_line_second_eval_data), notebook_line.create(
                    notebook_line_third_eval_data)

    # GENERA LAS COMPETENCIAS NORMALES + LINEA DE CUADERNO
    @api.multi
    def generate_son_competences(self, notebook_line_first_eval_comp, notebook_line_second_eval_comp, notebook_line_third_eval_comp):
        duplicated = self.check_duplicate_son_competence()
        if duplicated == None:
            son_competence_line = self.env['education.competence']
            son_competence_line_data = {'name': 'Son competence generated',
                                        'eval_mode': 'numeric',
                                        'evaluation_check': False,
                                        'global_check': False,
                                        }
            son_competence_created = son_competence_line.create(
                son_competence_line_data)
        else:
            son_competence_created = duplicated

        notebook_line = self.env['education.notebook.line']
        notebook_line_first_normal_data = {'planification_id': self.id,
                                           'description': 'Description for the son competence of the first evaluation in the notebook line',
                                           'eval_type': 'first',
                                           'competence_id': son_competence_created.id,
                                           'father_competence_id': notebook_line_first_eval_comp.id,
                                           'eval_percent': 33,
                                           }
        notebook_line_second_normal_data = {'planification_id': self.id,
                                            'description': 'Description for the son competence of the second evaluation in the notebook line',
                                            'eval_type': 'second',
                                            'competence_id': son_competence_created.id,
                                            'father_competence_id': notebook_line_second_eval_comp.id,
                                            'eval_percent': 33,
                                            }
        notebook_line_third_normal_data = {'planification_id': self.id,
                                           'description': 'Description for the son competence of the third evaluation in the notebook line',
                                           'eval_type': 'third',
                                           'competence_id': son_competence_created.id,
                                           'father_competence_id': notebook_line_third_eval_comp.id,
                                           'eval_percent': 33,
                                           }
        return notebook_line.create(
            notebook_line_first_normal_data), notebook_line.create(
                notebook_line_second_normal_data), notebook_line.create(
                    notebook_line_third_normal_data)

########################################UPDATE SONS###########################################################
    # ACTUALIZA LA LISTA DE NOTEBOOK LINES HIJOS
    @api.multi
    def update_son_competence_lines(self, notebook_line_global_comp, notebook_line_eval_first, notebook_line_eval_second, notebook_line_eval_third, notebook_line_son_first, notebook_line_son_second, notebook_line_son_third):
        eval_lines = [notebook_line_eval_first, notebook_line_eval_second, notebook_line_eval_third]
        for line in eval_lines:
            line.write({'education_notebook_line_id': notebook_line_global_comp.id})
        notebook_line_son_first.write({'education_notebook_line_id': notebook_line_eval_first.id})
        notebook_line_son_second.write({'education_notebook_line_id': notebook_line_eval_second.id})
        notebook_line_son_third.write({'education_notebook_line_id': notebook_line_eval_third.id})
###########################################################GENERATE RECORDS###############################################

    # GENERA LOS ACADEMIC RECORDS PARA LOS EXAMENES DE LA COMPETENCIA MASTER GLOBAL (PARA CADA NIÑO)
    @api.multi
    def generate_global_academic_record(self, n_line_id):
        kid_ids = n_line_id.planification_id.student_ids
        global_record = self.env['education.record']
        academic_record_line = self.env['education.record']

        for kid in kid_ids:
            academic_record_line_data = {'n_line_id': n_line_id.id,
                                         'kid_id': kid.id,
                                         }
            global_record = global_record + academic_record_line.create(
                academic_record_line_data)
        return global_record

    # GENERA LOS ACADEMIC RECORDS PARA LOS EXAMENES DE LAS COMPETENCIAS MASTER EVALUACION Y NORMALES(PARA CADA NIÑO)
    @api.multi
    def generate_evaluation_academic_records(self, notebook_line_eval_first, notebook_line_eval_second, notebook_line_eval_third, father_global_record_id, notebook_line_son_first, notebook_line_son_second, notebook_line_son_third):
        kid_first_ids = notebook_line_eval_first.planification_id.student_ids
        kid_second_ids = notebook_line_eval_second.planification_id.student_ids
        kid_third_ids = notebook_line_eval_third.planification_id.student_ids
        academic_record_line = self.env['education.record']
        academic_record_global_father = self.env['education.record']

        for kid in kid_first_ids:
            for global_father in father_global_record_id:
                if global_father.kid_id.id == kid.id:
                    academic_record_global_father = global_father
                    break
            academic_record_first_line_data = {'n_line_id': notebook_line_eval_first.id,
                                               'kid_id': kid.id,
                                               'father_record_id': academic_record_global_father.id,
                                               }
            first_eval_record = academic_record_line.create(academic_record_first_line_data)
            academic_record_first_son_line_data = {'n_line_id': notebook_line_son_first.id,
                                                   'kid_id': kid.id,
                                                   'father_record_id': first_eval_record.id,
                                                   }
            academic_record_line.create(academic_record_first_son_line_data)

        for kid in kid_second_ids:
            for global_father in father_global_record_id:
                if global_father.kid_id.id == kid.id:
                    academic_record_global_father = global_father
                    break
            academic_record_second_line_data = {'n_line_id': notebook_line_eval_second.id,
                                                'kid_id': kid.id,
                                                'father_record_id': academic_record_global_father.id,
                                                }
            second_eval_record = academic_record_line.create(academic_record_second_line_data)
            academic_record_second_son_line_data = {'n_line_id': notebook_line_son_second.id,
                                                    'kid_id': kid.id,
                                                    'father_record_id': second_eval_record.id,
                                                    }
            academic_record_line.create(academic_record_second_son_line_data)

        for kid in kid_third_ids:
            for global_father in father_global_record_id:
                if global_father.kid_id.id == kid.id:
                    academic_record_global_father = global_father
                    break
            academic_record_third_line_data = {'n_line_id': notebook_line_eval_third.id,
                                               'kid_id': kid.id,
                                               'father_record_id': academic_record_global_father.id,
                                               }
            third_eval_record = academic_record_line.create(academic_record_third_line_data)
            academic_record_third_son_line_data = {'n_line_id': notebook_line_son_third.id,
                                                   'kid_id': kid.id,
                                                   'father_record_id': third_eval_record.id,
                                                   }
            academic_record_line.create(academic_record_third_son_line_data)

###################################################################ACTION##################################################################
    # REALIZA TODAS LAS ACCIONES DE GENERACIÓN EN UNA FUNCIÓN
    @api.one
    def action_generate_master_competences(self):
        if self.master_competences_count == 0:
            # COMPETENCIAS + NOTEBOOK LINES
            notebook_line_global_comp = self.generate_global_competence()
            notebook_line_eval_first, notebook_line_eval_second, notebook_line_eval_third = self.generate_evaluation_competences(notebook_line_global_comp)
            notebook_line_son_first, notebook_line_son_second, notebook_line_son_third = self.generate_son_competences(notebook_line_eval_first, notebook_line_eval_second, notebook_line_eval_third)
            self.update_son_competence_lines(notebook_line_global_comp, notebook_line_eval_first, notebook_line_eval_second, notebook_line_eval_third, notebook_line_son_first, notebook_line_son_second, notebook_line_son_third)
            # RECORDS
            global_records = self.generate_global_academic_record(notebook_line_global_comp)
            self.generate_evaluation_academic_records(notebook_line_eval_first, notebook_line_eval_second, notebook_line_eval_third, global_records, notebook_line_son_first, notebook_line_son_second, notebook_line_son_third)
            # MARKS
            self.generate_numeric_marks()

    @api.one
    def action_generate_evaluations_for_courses_and_schools(self):
        evaluation_line = self.env['education.academic_year.evaluation']
        course_ids = self.env['education.course'].search([
            ('plan_id', '=', self.plan_id.id)])
        for course in course_ids:
            duplicated = self.check_duplicate_evaluations_for_courses_and_schools(course)
            if duplicated == None:
                first_evaluation_line_data = {'name': 'First evaluation generated',
                                              'a_year': self.academic_year_id.id,
                                              'date_start': '01-09-' + str(
                                                  self.academic_year_id.date_start.year) + '',
                                              'date_end': '25-12-' + str(
                                                  self.academic_year_id.date_end.year) + '',
                                              'course_id': course.id,
                                              'school_id': self.center_id.id,
                                              }
                second_evaluation_line_data = {'name': 'Second evaluation generated',
                                               'a_year': self.academic_year_id.id,
                                               'date_start': '10-01-' + str(
                                                   self.academic_year_id.date_end.year) + '',
                                               'date_end': '01-04-' + str(
                                                   self.academic_year_id.date_end.year) + '',
                                               'course_id': course.id,
                                               'school_id': self.center_id.id,
                                               }
                third_evaluation_line_data = {'name': 'Third evaluation generated',
                                              'a_year': self.academic_year_id.id,
                                              'date_start': '10-04-' + str(
                                                  self.academic_year_id.date_end.year) + '',
                                              'date_end': '01-07-' + str(
                                                  self.academic_year_id.date_end.year) + '',
                                              'course_id': course.id,
                                              'school_id': self.center_id.id,
                                              }
                evaluation_line.create(first_evaluation_line_data)
                evaluation_line.create(second_evaluation_line_data)
                evaluation_line.create(third_evaluation_line_data)
