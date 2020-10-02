# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
from odoo import fields, models


class DownloadEducationClassroom(models.TransientModel):
    _name = "download.education.classroom"
    _description = "Wizard to Download Classroom"

    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain=[("educational_category", "=", "school")], required=True)
    name = fields.Char(string="File name", readonly=True)
    data = fields.Binary(string="File", readonly=True)
    state = fields.Selection(
        selection=[
            ("open", "open"),
            ("get", "get"),
        ], string="State", default="open")

    def button_download_file(self):
        fname = "T06.txt"
        encode_string = ""
        for classroom in self.env["education.classroom"].search([
                ("center_id", "=", self.center_id.id)]):
            encode_string += "{:0>8}{:<50}{:0>3}\r".format(
                classroom.education_code, classroom.description,
                classroom.capacity)
        encode_string = encode_string.encode()
        file_bin = base64.encodebytes(encode_string)
        self.write({"state": "get", "data": file_bin, "name": fname})
        data_obj = self.env.ref(
            "hezkuntza.download_education_classroom_view_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "view_id": [data_obj.id],
            "res_id": self.id,
            "target": "new",
        }
