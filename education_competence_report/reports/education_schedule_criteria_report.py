# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs


class EducationScheduleCriteriaReport(models.Model):
    _name = 'education.schedule.criteria.report'
    _description = 'Education Schedule Criteria Report'
    _auto = False
    _rec_name = "schedule_id"
    _order = "schedule_id,student_id,education_criteria_id,competence_specific_id,education_record_id"

    schedule_id = fields.Many2one(
        comodel_name="education.schedule", string="Education Schedule")
    education_criteria_id = fields.Many2one(
        comodel_name="education.criteria", string="Education Criteria")
    competence_specific_id = fields.Many2one(
        comodel_name="education.competence.specific", string="Competence Specific")
    education_record_id = fields.Many2one(
        comodel_name="education.record", string="Education Record")
    exam_id = fields.Many2one(
        comodel_name="education.exam", string="Education Exam")
    student_id = fields.Many2one(
        comodel_name="res.partner", string="Student")
    numeric_mark = fields.Float(
        string="Official Mark",
        group_operator="avg",
    )

    def _select(self):
        select_str = """
            SELECT
                row_number() OVER () as id,
                sch.id AS schedule_id,
                stu.id AS student_id,
                exm.id AS exam_id,
                erec.id AS education_record_id,
                erec.numeric_mark AS numeric_mark,
                comp_spe.id AS competence_specific_id,
                crit.id AS education_criteria_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM education_schedule sch
                JOIN education_exam exm ON exm.schedule_id = sch.id
                JOIN education_record erec ON erec.exam_id = exm.id
                JOIN exam_edu_criteria_rel cri_rel ON cri_rel.exam_id = exm.id
                JOIN education_criteria crit ON crit.id = cri_rel.criteria_id
                JOIN education_competence_specific comp_spe ON comp_spe.id = crit.competence_specific_id
                JOIN res_partner stu ON stu.id = erec.student_id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                    GROUP BY sch.id, stu.id, exm.id, crit.id, comp_spe.id, erec.id
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
