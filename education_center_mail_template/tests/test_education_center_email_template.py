# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common
from odoo.exceptions import ValidationError


@common.at_install(False)
@common.post_install(True)
class TestEducationCenterEmailTemplate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestEducationCenterEmailTemplate, cls).setUpClass()
        cond = [('name', '=', 'mail_center_template')]
        center_view = cls.env['ir.ui.view'].search(cond, limit=1)
        cls.user = cls.env['res.users'].search([], limit=1)
        cls.email_template = cls.env.ref(
            'auth_signup.mail_template_user_signup_account_created')
        cls.email_template.center_template_id = center_view.id

    def test_education_center_email_template(self):
        with self.assertRaises(ValidationError):
            self.email_template.sudo().with_context(
                lang=self.user.lang).send_mail(self.user.id, force_send=True)
