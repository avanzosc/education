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
        'school_issue',
        'student_group_id'
    ):
        openupgrade.add_fields(
            env,
            [('student_group_id', 'school.issue', 'school_issue',
              'many2one', False, 'issue_education')]
        )
    cr.execute(
        """
        UPDATE school_issue i
        SET student_group_id = (
            SELECT current_group_id
            FROM res_partner p WHERE p.id = i.student_id);
        """)
