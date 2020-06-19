# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute(
        """
        ALTER TABLE education_notebook_template
        ADD COLUMN IF NOT EXISTS task_type_id INT
        """)
    cr.execute(
        """
        UPDATE education_notebook_template
        SET task_type_id = (
        SELECT id FROM education_task_type WHERE education_code = '0120')
        """)
