# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    group_type_codes = ['0001', '0002']
    group_type_obj = env['education.group_type']
    for group_code in group_type_codes:
        res = group_type_obj.search([('education_code', '=', group_code)])
        if res:
            openupgrade.add_xmlid(
                env.cr, 'hezkuntza',
                'education_group_type_{}'.format(group_code),
                'education.group_type', res.id, noupdate=False)
