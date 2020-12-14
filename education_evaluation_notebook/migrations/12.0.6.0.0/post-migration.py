# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    line_obj = env["education.notebook.line"]
    cr = env.cr
    global_lines = line_obj.search([("competence_id.global_check", "=", True)])
    for global_line in global_lines:
        cr.execute("""
            UPDATE education_notebook_line
            SET sequence = 0
            WHERE id = %s
            """, (global_line.id,))
    eval_lines = line_obj.search([
        ("competence_id.evaluation_check", "=", True)])
    for eval_line in eval_lines:
        if eval_line.eval_type == "first":
            eval_seq = 1
        elif eval_line.eval_type == "second":
            eval_seq = 2
        elif eval_line.eval_type == "third":
            eval_seq = 3
        else:
            eval_seq = 4
        cr.execute("""
            UPDATE education_notebook_line
            SET sequence = %s
            WHERE id = %s
            """, (eval_seq, eval_line.id,))
    for eval_line in eval_lines:
        sequence = 10
        for child_line in eval_line.child_line_ids:
            cr.execute("""
                UPDATE education_notebook_line
                SET sequence = %s
                WHERE id = %s
                """, (sequence, child_line.id,))
            sequence += 1
