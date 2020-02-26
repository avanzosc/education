# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        INSERT INTO
            education_subject_center
                (center_id, subject_id, lang_id, course_id, name)
        SELECT
            sch.center_id,
            sch.subject_id,
            sch.language_id,
            grp.course_id,
            sub.description
          FROM edu_schedule_group sch_group
          JOIN education_schedule sch
            ON sch_group.schedule_id = sch.id
          JOIN education_group grp
            ON sch_group.group_id = grp.id
          JOIN education_subject sub
            ON sub.id = sch.subject_id
         WHERE sch.subject_id IS NOT NULL
        GROUP BY
            sch.subject_id,
            sch.language_id,
            sch.center_id,
            grp.course_id,
            sub.description
        ON CONFLICT DO NOTHING;
    """)
