# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
from ._common import _convert_time_float_to_string
from odoo import fields, models


class DownloadEducationClassroom(models.TransientModel):
    _name = "download.education.resource"
    _description = "Wizard to Download Resources"

    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain=[("educational_category", "=", "school")], required=True)
    name = fields.Char(string="File name", readonly=True)
    data = fields.Binary(string="File", readonly=True)
    state = fields.Selection(
        selection=[
            ("open", "open"),
            ("get", "get"),
        ], string="Status", default="open")

    def button_download_file(self):
        fname = "T02.txt"
        encode_string = ""
        for calendar in self.env['resource.calendar'].search([
                ("center_id", "=", self.center_id.id)]):
            encode_string += "1{:0>8}{:<50}\r".format(
                calendar.education_code, calendar.name)
            for attendance in calendar.attendance_ids.sorted(
                    key=lambda a: (a.dayofweek_education, a.daily_hour)):
                encode_string += "2{:0>2}{}{}{}{}\r".format(
                    attendance.daily_hour, attendance.dayofweek_education,
                    _convert_time_float_to_string(attendance.hour_from),
                    _convert_time_float_to_string(attendance.hour_to),
                    (1 if attendance.recess else 0))
        encode_string = encode_string.encode()
        file_bin = base64.encodebytes(encode_string)
        self.write({"state": "get", "data": file_bin, "name": fname})
        data_obj = self.env.ref(
            "hezkuntza.download_education_resource_view_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "view_id": [data_obj.id],
            "res_id": self.id,
            "target": "new",
        }
