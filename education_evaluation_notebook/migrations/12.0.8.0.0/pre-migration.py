# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        CREATE TABLE IF NOT EXISTS competence_type_n_line_rel(
            n_line_id INT,
            competence_type_id INT
        );
    """)
    cr.execute("""
        INSERT INTO
            competence_type_n_line_rel
                (n_line_id, competence_type_id)
        SELECT
            n_line.id,
            ect.id
          FROM education_notebook_line n_line
          JOIN education_competence_type ect
            ON n_line.competence_type_id = ect.id
        GROUP BY
            n_line.id,
            ect.id
        ON CONFLICT DO NOTHING;
    """)
