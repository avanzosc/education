# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    alumni = env["res.partner"].search([
        ("alumni_center_id", "!=", False),
        ("alumni_academic_year_id", "!=", False),
        ("alumni_course_id", "=", False),
    ])
    for alumnus in alumni:
        group = alumnus.student_group_ids.filtered(
            lambda g: g.academic_year_id == alumnus.alumni_academic_year_id and
            g.center_id == alumnus.alumni_center_id and
            g.group_type_id.type == "official")
        if group:
            cr.execute("""
                UPDATE res_partner
                SET alumni_course_id = %s
                WHERE id = %s
            """, (group.course_id.id, alumnus.id,))
