# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(
        cr,
        'education_record',
        'excepcionality'
    ):
        openupgrade.add_fields(
            env,
            [('exceptionality', 'education.record', 'education_record',
              'selection', False, 'education_evaluation_notebook')]
        )
    cr.execute(
        """
        UPDATE education_record
        SET exceptionality = 'exempt', state = 'initial'
        WHERE state = 'exempt';
        """)
    cr.execute(
        """
        UPDATE education_record
        SET exceptionality = 'not_taken', state = 'initial'
        WHERE state = 'not_taken';
        """)
    cr.execute(
        """
        UPDATE education_record
        SET state = 'initial'
        WHERE state = 'not_evaluated' OR state IS NULL;
        """)
