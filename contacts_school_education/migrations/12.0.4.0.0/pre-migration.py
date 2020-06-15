# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    res = env["education.task_type"].search([("education_code", "=", "0120")])
    if res:
        openupgrade.add_xmlid(
            env.cr, "contacts_school_education", "education_task_type_0120",
            "education.task_type", res.id, noupdate=False)
