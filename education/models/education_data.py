# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re

from odoo import api, fields, models
from odoo.osv import expression


class EducationData(models.AbstractModel):
    _name = 'education.data'
    _description = 'Education Data Base Model'
    _rec_name = 'description'
    _order = 'education_code'

    education_code = fields.Char(
        string='Education Code', required=True, copy=False)
    description = fields.Text(
        string='Description', required=True)
    short_description = fields.Char(
        string='Short Description')
    active = fields.Boolean('Active', default=True)

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            result.append((record.id, '[{}] {}'.format(
                record.education_code, record.description)))
        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        """Include education code in direct name or description search."""
        args = expression.normalize_domain(args)
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if (arg[0] == 'name' or arg[0] == 'display_name' or
                        arg[0] == self._rec_name):
                    index = args.index(arg)
                    args = (
                        args[:index] + ['|',
                                        ('education_code', arg[1], arg[2])] +
                        args[index:]
                    )
                    break
        return super(EducationData, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)

    def get_report_file_name(self):
        return '{}-{}'.format(
            self.education_code, re.sub(r'[\W_]+', '', self.description))
