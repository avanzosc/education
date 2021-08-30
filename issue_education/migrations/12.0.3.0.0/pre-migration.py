# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(
        cr,
        'school_claim',
        'student_group_id'
    ):
        openupgrade.add_fields(
            env,
            [('student_group_id', 'school.claim', 'school_claim',
              'many2one', False, 'issue_education')]
        )
    cr.execute(
        """
        UPDATE school_claim c
        SET student_group_id = (
            SELECT student_group_id
              FROM school_issue i
             WHERE c.id = i.claim_id
             LIMIT 1);
        """)
