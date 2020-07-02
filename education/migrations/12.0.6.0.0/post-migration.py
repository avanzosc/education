# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        UPDATE education_subject_center c
        SET subject_type = (
            SELECT subject_type
            FROM education_subject s
            WHERE s.id = c.subject_id);
    """)
