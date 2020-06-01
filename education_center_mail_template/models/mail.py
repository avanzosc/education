# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    center_template_id = fields.Many2one(
        string='Center template', comodel_name='ir.ui.view')

    @api.multi
    def send_mail(self, res_id, force_send=False, raise_exception=False,
                  email_values=None, notif_layout=False):
        use_center_template = False
        if self.center_template_id:
            notif_layout = self.center_template_id.key
            use_center_template = True
        return super(MailTemplate, self.with_context(
            use_center_template=use_center_template)).send_mail(
                res_id, force_send=force_send, raise_exception=raise_exception,
                email_values=email_values, notif_layout=notif_layout)
