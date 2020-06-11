# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    official_groups = env["education.group"].search([
        ("group_type_id.type", "=", "official"),
        ("academic_year_id.current", "=", True),
    ])
    for official_group in official_groups:
        for partner in official_group.student_ids:
            cr.execute("""
                UPDATE res_partner
                SET current_group_id = %s,
                current_center_id = %s
                WHERE id = %s
            """, (official_group.id, official_group.center_id.id, partner.id,))
            if official_group.course_id:
                cr.execute("""
                    UPDATE res_partner
                    SET current_course_id = %s
                    WHERE id = %s
                """, (official_group.course_id.id, partner.id,))
