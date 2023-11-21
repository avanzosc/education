# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs
from odoo.addons.education_evaluation_notebook.models. \
    education_academic_year_evaluation import EVAL_TYPE


class EducationStudentCriteriaReport(models.Model):
    _name = "education.student.criteria.report"
    _description = "Education Group Criteria Report"
    _auto = False
    _rec_name = "student_id"
    _order = "student_id,competence_profile_id,competence_type_id"

    competence_type_id = fields.Many2one(
        comodel_name="education.competence.type",
        string="Competence Type",
    )
    competence_profile_id = fields.Many2one(
        comodel_name="education.competence.profile",
        string="Competence Profile"
    )
    education_record_id = fields.Many2one(
        comodel_name="education.record",
        string="Education Record",
    )
    exam_id = fields.Many2one(
        comodel_name="education.exam",
        string="Education Exam",
    )
    student_id = fields.Many2one(
        comodel_name="res.partner",
        string="Student",
    )
    numeric_mark = fields.Float(
        string="Official Mark",
        group_operator="avg",
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        string="Academic Year",
    )
    eval_type = fields.Selection(
        selection=EVAL_TYPE,
        string="Evaluation Season",
    )

    def _select(self):
        select_str = """
            SELECT
                row_number() OVER () as id,
                rec.id AS education_record_id,
                rec.numeric_mark AS numeric_mark,
                rec.student_id AS student_id,
                rec.exam_id AS exam_id,
                rec.academic_year_id AS academic_year_id,
                rec.eval_type AS eval_type,
                type.id AS competence_type_id,
                type.competence_profile_id AS competence_profile_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM education_record rec
                JOIN education_exam exm ON exm.id = rec.exam_id
                JOIN exam_edu_criteria_rel cri_rel ON cri_rel.exam_id = exm.id
                JOIN education_criteria cri ON cri.id = cri_rel.criteria_id
                JOIN education_competence_specific spe ON spe.id = cri.competence_specific_id
                JOIN edu_comp_specific_type_rel spe_rel ON spe_rel.comp_specific_id = spe.id
                JOIN education_competence_type type ON spe_rel.comp_type_id = type.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                    GROUP BY
                        rec.id,
                        rec.student_id,
                        rec.exam_id,
                        rec.academic_year_id,
                        rec.eval_type,
                        type.id,
                        type.competence_profile_id
                """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as
                (
                %s %s %s
            )""", (
                AsIs(self._table), AsIs(self._select()), AsIs(self._from()),
                AsIs(self._group_by()),))
