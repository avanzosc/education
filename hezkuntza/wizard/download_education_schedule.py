# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
from ._common import _convert_time_float_to_string
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class DownloadEducationClassroom(models.TransientModel):
    _name = "download.education.schedule"
    _description = "Wizard to Download Schedule"

    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain=[("educational_category", "=", "school")], required=True)
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year", string="Academic Year",
        default=lambda self: self.env[
            "education.academic_year"].search([("current", "=", True)]),
        required=True)
    name = fields.Char(string="File name", readonly=True)
    data = fields.Binary(string="File", readonly=True)
    name_student = fields.Char(string="File name", readonly=True)
    data_student = fields.Binary(string="File", readonly=True)
    warning_msg = fields.Html(string="Warning", readonly=True)
    state = fields.Selection(
        selection=[
            ("open", "open"),
            ("get", "get"),
        ], string="State", default="open")

    def button_download_file(self):
        fname_schedule = "cuadrohorario.txt"
        anonymus_teacher = self.env.ref("education.hr_employee_anonymous")
        if not self.center_id.education_code:
            raise ValidationError(
                _("Education Center must have Education Code defined"))
        encode_string = "1CH{:0>6}{:0>4}\r".format(
            self.center_id.education_code, self.academic_year_id.name[:4])
        warning_msg = ""
        errored_teacher = self.env["hr.employee"]
        for schedule in self.env["education.schedule"].search([
                ("center_id", "=", self.center_id.id),
                ("academic_year_id", "=", self.academic_year_id.id),
                ("teacher_id", "!=", anonymus_teacher.id),
                ("timetable_ids", "!=", False)]):
            schedule_msg = ""
            if not schedule.classroom_id:
                schedule_msg += _("<dd>Must have defined a classroom.</dd>\n")
            if (not schedule.teacher_id.edu_idtype_id.education_code or
                    not schedule.teacher_id.identification_id):
                errored_teacher |= schedule.teacher_id
            for timetable in schedule.timetable_ids:
                encode_string += (
                    "2{:0>4}{:<15}{:0>2}{}{:0>4}{}{}{:0>8}".format(
                        schedule.teacher_id.edu_idtype_id.education_code,
                        schedule.teacher_id.identification_id,
                        timetable.attendance_id.daily_hour,
                        timetable.attendance_id.dayofweek_education,
                        schedule.task_type_id.education_code,
                        _convert_time_float_to_string(
                            timetable.attendance_id.hour_from),
                        _convert_time_float_to_string(
                            timetable.attendance_id.hour_to),
                        schedule.classroom_id.education_code))
                if schedule.task_type_id.type == "L":
                    encode_string += "{:0>8}{}{:0>2}\r".format(
                        schedule.subject_id.education_code,
                        (schedule.subject_type and schedule.subject_type[:1] or
                         ""),
                        schedule.language_id.education_code)
                elif schedule.task_type_id.type == "N":
                    encode_string += "{:0>3}{:0>4}{:0>4}\r".format(
                        schedule.activity_type_id.education_code,
                        schedule.level_id.education_code,
                        schedule.plan_id.education_code)
                for group in schedule.group_ids:
                    parent = group.parent_id or group
                    encode_string += "3{:0>8}0000{:0>4}{:<50}{:0>8}\r".format(
                        group.education_code, group.student_count,
                        group.description, parent.education_code)
            if schedule_msg:
                warning_msg += "<dl><dt>{}</dt>\n{}</dl>".format(
                    schedule.display_name, schedule_msg)
        for teacher in errored_teacher:
            warning_msg += _(
                "Teacher {} must have identification type and number."
                "<br/>\n").format(teacher.display_name)
        encode_string = encode_string.encode()
        schedule_file_bin = base64.encodebytes(encode_string)
        self.write({
            "state": "get",
            "data": schedule_file_bin,
            "name": fname_schedule,
            "warning_msg": warning_msg,
        })
        data_obj = self.env.ref(
            "hezkuntza.download_education_schedule_view_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "view_id": [data_obj.id],
            "res_id": self.id,
            "target": "new",
        }
