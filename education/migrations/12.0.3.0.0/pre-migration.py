# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        SELECT DISTINCT(type) AS subject_type
          FROM education_subject;
    """)
    for subject_type in cr.fetchall():
        cr.execute("""
            INSERT INTO education_subject_type
                (education_code, description, active)
            VALUES ('%s', '%s', True) ON CONFLICT DO NOTHING;""" %
                   (subject_type[0], subject_type[0]))
    cr.execute("""
        UPDATE education_subject AS s
        SET type_id = (SELECT id FROM education_subject_type AS t WHERE
        t.education_code = s.type LIMIT 1);
    """)
