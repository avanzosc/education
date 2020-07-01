# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        ALTER TABLE education_subject_center
        ADD COLUMN level_id integer;
    """)
    cr.execute("""
        ALTER TABLE education_subject_center
        RENAME TO education_subject_center_name2;
    """)
    cr.execute("""
        UPDATE education_subject_center_name2 n
        SET level_id = (
            SELECT level_id
            FROM education_group g
            WHERE g.center_id = n.center_id
            AND g.course_id = n.course_id
            LIMIT 1);
    """)
