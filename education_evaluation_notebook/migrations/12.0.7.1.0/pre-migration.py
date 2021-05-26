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
        'exam_eval_percent'
    ):
        cr.execute(
            """
            ALTER TABLE education_record
            ADD COLUMN exam_eval_percent numeric;
            """)
    cr.execute(
        """
        UPDATE education_record r
        SET exam_eval_percent = (
            SELECT eval_percent
            FROM education_exam e
            WHERE e.id = r.exam_id)
        WHERE exam_id IS NOT NULL;
        """)
    cr.execute(
        """
        UPDATE education_record r
        SET exam_eval_percent = (
            SELECT eval_percent
            FROM education_notebook_line l
            WHERE l.id = r.n_line_id)
        WHERE exam_id IS NULL;
        """)
