# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
from ._common import _convert_time_float_to_string, HEZKUNTZA_ENCODING
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class DownloadEducationClassroom(models.TransientModel):
    _name = "download.education.group"
    _description = "Wizard to Download Groups"

    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain=[("educational_category", "=", "school")], required=True)
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year", string="Academic Year",
        default=lambda self: self.env[
            "education.academic_year"].search([("current", "=", True)]),
        required=True)
    level_id = fields.Many2one(
        comodel_name="education.level", string="Education Level",
        required=True)
    course_id = fields.Many2one(
        comodel_name="education.course", string="Course", required=True)
    name = fields.Char(string="File name", readonly=True)
    data = fields.Binary(string="File", readonly=True)
    name_student = fields.Char(string="File name", readonly=True)
    data_student = fields.Binary(string="File", readonly=True)
    warning_msg = fields.Html(string="Warning", readonly=True)
    state = fields.Selection(
        selection=[
            ("open", "open"),
            ("get", "get"),
        ], string="Status", default="open")

    def button_download_file(self):
        self.ensure_one()
        fname_group = "grupos.txt"
        fname_student = "T27.txt"
        if not self.center_id.education_code:
            raise ValidationError(
                _("Education Center must have Education Code defined"))
        encode_string = "1GR{:0>6}{:0>4}\r".format(
            self.center_id.education_code, self.academic_year_id.name[:4])
        student_string = ""
        warning_msg = ""
        code_missing = self.env["res.partner"]
        for group in self.env["education.group"].search([
                ("center_id", "=", self.center_id.id),
                ("academic_year_id", "=", self.academic_year_id.id),
                ("level_id", "=", self.level_id.id),
                ("course_id", "=", self.course_id.id),
                ("student_count", "!=", 0),
                ("group_type_id.type", "in", ["official", "class"])]):
            group_msg = ""
            if not group.classroom_id:
                group_msg += _("<dd>Must have defined a classroom.</dd>\n")
            if not group.shift_id:
                group_msg += _("<dd>Must have defined a shift.</dd>\n")
            if not group.course_id:
                group_msg += _("<dd>Must have defined a course.</dd>\n")
            if not group.model_id:
                group_msg += _(
                    "<dd>Must have defined an educational model.</dd>\n")
            encode_string += (
                "2{:0>8}{:<50}{:0>4}{:0>4}{:0>4}{:0>4}{:0>4}{:0>4}{:0>4}"
                "{:0>8}".format(
                    group.education_code,
                    group.description.replace("\n", " "),
                    group.plan_id.education_code,
                    group.level_id.education_code,
                    group.field_id.education_code,
                    group.shift_id.education_code,
                    group.course_id.education_code,
                    group.model_id.education_code,
                    group.group_type_id.education_code,
                    group.calendar_id.education_code))
            for i in range(1, 11):
                teacher = group.teacher_ids.filtered(lambda t: t.sequence == i)
                if (i == 1 and group.group_type_id.type == "official" and
                        not teacher):
                    group_msg += _(
                        "<dd>Must have defined a teacher with sequence 1."
                        "</dd>\n")
                encode_string += "{:0>4}{:<15}".format(
                    teacher.employee_id.edu_idtype_id.education_code or "",
                    teacher.employee_id.identification_id or "")
            encode_string += "{:0>4}{:<250}{:0>8}\r".format(
                group.student_count, group.comments,
                group.classroom_id.education_code)
            for attendance in group.calendar_session_ids.sorted(
                    key=lambda a: (a.daily_hour, a.dayofweek_education)):
                encode_string += "3{:0>8}{:0>2}{}{}{}{}\r".format(
                    group.education_code, attendance.daily_hour,
                    attendance.dayofweek_education,
                    _convert_time_float_to_string(attendance.hour_from),
                    _convert_time_float_to_string(attendance.hour_to),
                    (1 if attendance.recess else 0))
            if group_msg:
                warning_msg += "<dl><dt>{}</dt>\n{}</dl>".format(
                    group.display_name, group_msg)
            for student in group.student_ids:
                if not student.education_code:
                    code_missing |= student
                else:
                    student_string += "{:0>8}{:0>10}\r".format(
                        group.education_code, student.education_code)
        for student_missing in code_missing:
            warning_msg += _("{} missing education code<br/>\n").format(
                student_missing.display_name)
        encode_string = encode_string.encode(HEZKUNTZA_ENCODING, "replace")
        group_file_bin = base64.encodebytes(encode_string)
        student_string = student_string.encode()
        student_file_bin = base64.encodebytes(student_string)
        self.write({
            "state": "get",
            "data": group_file_bin,
            "data_student": student_file_bin,
            "name": fname_group,
            "name_student": fname_student,
            "warning_msg": warning_msg,
        })
        data_obj = self.env.ref(
            "hezkuntza.download_education_group_view_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "view_id": [data_obj.id],
            "res_id": self.id,
            "target": "new",
        }
