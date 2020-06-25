# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        UPDATE res_partner p
        SET current_level_id = (
            SELECT g.level_id FROM education_group g
            WHERE g.id = p.current_group_id
        ) WHERE p.current_group_id IS NOT Null
            AND current_level_id IS Null;
    """)
