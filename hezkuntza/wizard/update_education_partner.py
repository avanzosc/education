# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.models import expression
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
import base64

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None


class UpdateEducationResPartner(models.TransientModel):
    _name = "update.education.partner"
    _description = "Wizard to Update Partner Education Code"

    file = fields.Binary(
        string="Student Information File", filters="*.xls")
    file_line_ids = fields.One2many(
        comodel_name="update.education.partner.line", inverse_name="wizard_id",
        string="Lines")
    partner_line_ids = fields.One2many(
        comodel_name="update.education.partner.line", inverse_name="wizard_id",
        string="Partner Lines", domain=[("partner_id", "!=", False)])
    missing_partner_line_ids = fields.One2many(
        comodel_name="update.education.partner.line", inverse_name="wizard_id",
        string="Missing Partner Lines",
        domain=[("missing_partner", "=", True)])
    duplicated_partner_line_ids = fields.One2many(
        comodel_name="update.education.partner.line", inverse_name="wizard_id",
        string="Duplicated Partner Lines",
        domain=[("duplicated_partner", "=", True)])
    partner_count = fields.Integer(
        compute="_compute_partner_count", store=True)
    missing_partner_count = fields.Integer(
        compute="_compute_partner_count", store=True)
    duplicated_partner_count = fields.Integer(
        compute="_compute_partner_count", store=True)

    @api.depends("file_line_ids")
    def _compute_partner_count(self):
        for wizard in self:
            wizard.partner_count = len(
                wizard.file_line_ids.filtered("partner_id"))
            wizard.missing_partner_count = len(
                wizard.file_line_ids.filtered("missing_partner"))
            wizard.duplicated_partner_count = len(
                wizard.file_line_ids.filtered("duplicated_partner"))

    @api.multi
    def upload_file(self):
        self.ensure_one()
        if self.file:
            self.file_line_ids.unlink()
            book = base64.decodestring(self.file)
            reader = xlrd.open_workbook(file_contents=book)
            try:
                sheet = reader.sheet_by_name("Modulos-Matricula-Alumno")
                line_obj = self.env["update.education.partner.line"]
                # keys = [c.value for c in sheet.row(1)]
                for counter in range(2, sheet.nrows-1):
                    rowValues = sheet.row_values(
                        counter, 0, end_colx=sheet.ncols)
                    # values = dict(zip(keys, rowValues))
                    line_data = {
                        "wizard_id": self.id,
                        # COD_ALU
                        "student_education_code": rowValues[6].zfill(10),
                        # DOCU_IDENTI_ALU
                        "student_document": rowValues[8],
                        # APELLIDO_1_ALU
                        "student_lastname1": rowValues[9],
                        # APELLIDO_2_ALU
                        "student_lastname2": rowValues[10],
                        # NOMBRE_ALU
                        "student_name": rowValues[11],
                    }
                    line_obj.find_or_create(line_data)
            except Exception:
                raise ValidationError(_('This is not a valid file.'))

    @api.multi
    def button_update_education_code(self):
        self.mapped("file_line_ids").button_update_education_code()

    @api.multi
    def button_update_vat(self):
        self.mapped("file_line_ids").button_update_vat()

    @api.multi
    def button_update_education_code_and_vat(self):
        self.mapped("file_line_ids").button_update_education_code_and_vat()


class UpdateEducationResPartnerLine(models.TransientModel):
    _name = "update.education.partner.line"
    _description = "Wizard Lines to Update Partner Education Code"
    _order = "student_lastname1, student_lastname2, student_name"

    wizard_id = fields.Many2one(
        comodel_name="update.education.partner", string="Wizard",
        required=True)
    student_education_code = fields.Char(
        string="Student Education Code", required=True)
    student_document = fields.Char(string="ID Document")
    student_lastname1 = fields.Char(string="Student Last Name", required=True)
    student_lastname2 = fields.Char(string="Student Second Last Name")
    student_name = fields.Char(string="Student First Name", required=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner", compute="_compute_partner",
        string="Partner", store=True)
    missing_partner = fields.Boolean(
        compute="_compute_partner", store=True)
    duplicated_partner = fields.Boolean(
        compute="_compute_partner", store=True)
    education_code = fields.Char(
        related="partner_id.education_code", string="Partner Education Code")
    vat = fields.Char(
        related="partner_id.vat", string="Partner Tax ID")

    @api.depends("student_document", "student_lastname1", "student_lastname2",
                 "student_name", "student_education_code")
    def _compute_partner(self):
        for line in self:
            partners = line._find_partner_ids()
            if len(partners) > 1:
                partners = (
                    partners.filtered(
                        lambda p: p.education_code ==
                        line.student_education_code)
                    or partners.filtered(lambda p: not p.education_code))
            line.missing_partner = (len(partners) == 0)
            line.duplicated_partner = (len(partners) > 1)
            line.partner_id = partners[:1] if len(partners) == 1 else False

    def _find_partner_ids(self):
        self.ensure_one()
        partners = partner_obj = self.env["res.partner"]
        if self.student_document:
            partners = partner_obj.search([
                ("vat", "ilike", self.student_document)])
        if not partners:
            partners = partner_obj.search([
                ("lastname", "=ilike", self.student_lastname1.encode("utf-8")),
                ("lastname2", "=ilike", self.student_lastname2.encode("utf-8")),
                ("firstname", "=ilike", self.student_name.encode("utf-8")),
            ])
        return partners

    def find_or_create(self, values):
        line = self.search([
            ("wizard_id", "=", values["wizard_id"]),
            ("student_education_code", "=", values["student_education_code"]),
            ("student_document", "=", values["student_document"]),
            ("student_lastname1", "=", values["student_lastname1"]),
            ("student_lastname2", "=", values["student_lastname2"]),
            ("student_name", "=", values["student_name"]),
        ])
        if not line:
            self.create(values)

    @api.multi
    def button_update_education_code(self):
        for line in self.filtered("partner_id"):
            line.partner_id.education_code = line.student_education_code

    @api.multi
    def button_update_vat(self):
        for line in self.filtered(
                lambda l: l.partner_id and l.student_document):
            try:
                line.partner_id.vat = "ES{}".format(line.student_document)
            except Exception:
                pass

    @api.multi
    def button_update_education_code_and_vat(self):
        self.button_update_education_code()
        self.button_update_vat()
        return True

    @api.multi
    def button_show_partners(self):
        self.ensure_one()
        partners = self._find_partner_ids()
        action = self.env.ref("contacts.action_contacts")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("id", "in", partners.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
