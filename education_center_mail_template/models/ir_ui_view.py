# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, api, _
from odoo.exceptions import ValidationError


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.multi
    def render(self, values=None, engine='ir.qweb', minimal_qcontext=False):
        ir_model_obj = self.env['ir.model']
        if ('use_center_template' in self.env.context and
            self.env.context.get('use_center_template', False) and
                values and 'record' in values):
            record = values.get('record')
            cond = [('model', '=', record._name)]
            ir_model = ir_model_obj.search(cond, limit=1)
            if ir_model and any(
                    [x.name == 'center_id' for x in ir_model.field_id]):
                values['center'] = record.center_id
            else:
                error = _(u'Field "center_id" does not exist in model'
                          ' {}').format(record._name)
                raise ValidationError(error)
        return super(IrUiView, self).render(
            values, engine=engine, minimal_qcontext=minimal_qcontext)
