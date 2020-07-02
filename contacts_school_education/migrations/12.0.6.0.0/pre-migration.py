# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute(
        """
        UPDATE res_partner_permission AS p
        SET center_id = (
            SELECT current_center_id
              FROM res_partner AS c
             WHERE c.id = p.partner_id)
        WHERE center_id IS NULL;
        """)
    cr.execute(
        """
        INSERT INTO education_subject_center
            (center_id, course_id, level_id, subject_id)
        SELECT
            c.next_school_id,
            c.next_course_id,
            s.level_id,
            r.education_subject_id
        FROM education_course_change_education_subject_rel r
        JOIN education_course_change c
        ON c.id = r.education_course_change_id
        JOIN education_course s
        ON s.id = c.next_course_id
        ON CONFLICT DO NOTHING;
        """)
