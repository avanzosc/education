# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from ._common import _read_binary_file, _format_info
from odoo import _, exceptions, fields, models


class UploadEducationContractType(models.TransientModel):
    _name = 'upload.education.contract_type'
    _description = 'Wizard to Upload Education Contract Types'

    file = fields.Binary(
        string='Contract Types File (T31)', filters='*.txt')

    def button_upload(self):
        lines = _read_binary_file(self.file)
        contract_type_obj = self.env['education.contract_type']
        if not lines:
            raise exceptions.Warning(_('Empty file.'))
        else:
            for line in lines:
                if len(line) > 0:
                    education_code = _format_info(line[0:4])
                    vals = {
                        'education_code': education_code,
                        'description': _format_info(line[4:104]),
                        'description_eu': _format_info(line[104:204]),
                        'short_description': _format_info(line[204:224]),
                        'short_description_eu': _format_info(line[224:244]),
                    }
                    contract_types = contract_type_obj.search([
                        ('education_code', '=', education_code)])
                    if contract_types:
                        contract_types.write(vals)
                    else:
                        contract_type_obj.create(vals)
        action = self.env.ref('education.action_education_contract_type')
        return action.read()[0]
