# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute(
        """
        UPDATE calendar_event e
           SET academic_year_id = (
            SELECT academic_year_id
              FROM school_claim c
             WHERE c.id = e.res_id
             LIMIT 1)
         WHERE e.res_model = 'school.claim'
           AND e.academic_year_id IS NULL;
        """)
    events = env["calendar.event"].search([
        ("res_model", "=", "school.claim")])
    for event in events:
        group = event.student_id.get_current_group(event.academic_year_id)
        cr.execute(
            """
            UPDATE calendar_event e
               SET course_id = %s,
                   center_id = %s
             WHERE e.id = %s
            """, (group.course_id.id, group.center_id.id, event.id))
