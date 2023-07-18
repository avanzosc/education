# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs


class EducationGroupCompetenceReport(models.Model):
    _name = 'education.group.competence.report'
    _description = 'Education Group Competence Report'
    _auto = False
    _rec_name = "group_id"
    _order = "schedule_id,student_id,n_line_id,competence_type_id,education_record_id"

    group_id = fields.Many2one(
        'education.group', 'Education Group')
    schedule_id = fields.Many2one(
        comodel_name="education.schedule", string="Education Schedule")
    student_id = fields.Many2one(
        'res.partner', 'Student')
    education_record_id = fields.Many2one(
        'education.record', string='Education Record')
    numeric_mark = fields.Float(
        string="Official Mark",
        group_operator="avg",
    )
    competence_specific_id = fields.Many2one(
        comodel_name="education.competence.specific", string="Competence Specific")
    competence_type_id = fields.Many2one(
        comodel_name="education.competence.type", string="Competence Type")
    n_line_id = fields.Many2one(
        comodel_name="education.notebook.line", string="Notebook Line")
    competence_profile_id = fields.Many2one(
        comodel_name="education.competence.profile", string="Notebook Line")

    def _select(self):
        select_str = """
            SELECT
                row_number() OVER () as id,
                grp.id AS group_id,
                sch.schedule_id AS schedule_id,
                stu.id AS student_id,
                ntbl.id AS n_line_id,
                erec.id AS education_record_id,
                erec.numeric_mark AS numeric_mark,
                cspe.id AS competence_specific_id,
                ctrel.competence_type_id AS competence_type_id,
                ecp.id AS competence_profile_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM education_group grp
                JOIN edu_schedule_group as sch ON grp.id = sch.group_id
                JOIN education_notebook_line ntbl ON ntbl.schedule_id = sch.schedule_id
                JOIN competence_type_n_line_rel ctrel ON ctrel.n_line_id = ntbl.id
                JOIN education_competence_type ect ON ctrel.competence_type_id = ect.id
                JOIN edu_comp_specific_type_rel sp_typ_rel ON sp_typ_rel.comp_type_id = ect.id
                JOIN education_competence_specific cspe ON sp_typ_rel.comp_specific_id = cspe.id
                JOIN education_competence_profile ecp ON ect.competence_profile_id = ecp.id
                JOIN education_record erec ON erec.n_line_id = ntbl.id
                JOIN res_partner stu ON stu.id = erec.student_id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY grp.id, sch.schedule_id, stu.id, ntbl.id, cspe.id, ctrel.competence_type_id, ecp.id, erec.id
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
