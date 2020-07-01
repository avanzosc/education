# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        INSERT INTO
            education_subject_center
                (center_id, level_id, course_id, subject_id)
        SELECT
            n.center_id,
            n.level_id,
            n.course_id,
            n.subject_id
          FROM education_subject_center_name2 n
        GROUP BY
            n.center_id,
            n.level_id,
            n.course_id,
            n.subject_id
        ON CONFLICT DO NOTHING;
    """)
    cr.execute("""
        INSERT INTO
            education_subject_center_name
                (name, subject_center_id, lang_id)
        SELECT
            n.name,
            c.id,
            n.lang_id
          FROM education_subject_center_name2 n
          JOIN education_subject_center c
            ON c.center_id = n.center_id
            AND c.level_id = n.level_id
            AND c.course_id = n.course_id
            AND c.subject_id = n.subject_id
        GROUP BY
            n.name, n.lang_id, c.id
        ON CONFLICT DO NOTHING;
    """)
    cr.execute("""
        DROP TABLE education_subject_center_name2;
    """)
