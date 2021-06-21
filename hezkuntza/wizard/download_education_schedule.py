# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
from ._common import _convert_time_float_to_string, HEZKUNTZA_ENCODING
from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.models import expression


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
    level_id = fields.Many2one(
        comodel_name="education.level", string="Education Level")
    course_ids = fields.Many2many(
        comodel_name="education.course", string="Course")
    teacher_id = fields.Many2one(
        comodel_name="hr.employee", string="Teacher")
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
        fname_schedule = "cuadrohorario.txt"
        anonymus_teacher = self.env.ref("education.hr_employee_anonymous")
        if not self.center_id.education_code:
            raise ValidationError(
                _("Education Center must have Education Code defined"))
        encode_string = "1CH{:0>6}{:0>4}\r".format(
            self.center_id.education_code, self.academic_year_id.name[:4])
        warning_msg = ""
        errored_teacher = self.env["hr.employee"]
        group_domain = [
                ("center_id", "=", self.center_id.id),
                ("academic_year_id", "=", self.academic_year_id.id),
                ("student_count", "!=", 0),
                ("group_type_id.type", "in", ["official", "class"]),
        ]
        if self.level_id:
            group_domain = expression.AND(
                [group_domain, [("level_id", "=", self.level_id.id)]])
        if self.course_ids:
            group_domain = expression.AND(
                [group_domain, [("course_id", "in", self.course_ids.ids)]])
        groups = self.env["education.group"].search(group_domain)
        schedule_domain = [
                ("center_id", "=", self.center_id.id),
                ("academic_year_id", "=", self.academic_year_id.id),
                ("teacher_id", "!=", anonymus_teacher.id),
                ("timetable_ids", "!=", False),
                ("group_ids", "in", groups.ids),
        ]
        if self.teacher_id:
            schedule_domain = expression.AND(
                [schedule_domain, [("teacher_id", "=", self.teacher_id.id)]])
        for schedule in self.env["education.schedule"].search(schedule_domain):
            schedule_msg = ""
            if not schedule.classroom_id:
                schedule_msg += _("<dd>Must have defined a classroom.</dd>\n")
            if (not schedule.teacher_id.edu_idtype_id.education_code or
                    not schedule.teacher_id.identification_id):
                errored_teacher |= schedule.teacher_id
            for timetable in schedule.timetable_ids:
                schedule_string = (
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
                    levels = schedule.mapped("group_ids.level_id")
                    schedule_string += "{:0>8}{}{:0>2}000{:0>4}{:0>4}\r".format(
                        schedule.subject_id.education_code,
                        (schedule.subject_type and schedule.subject_type[:1] or
                         " "),
                        schedule.language_id.education_code,
                        levels[:1].education_code,
                        levels[:1].plan_id.education_code
                    )
                elif schedule.task_type_id.type == "N":
                    schedule_string += "00000000 00{:0>3}{:0>4}{:0>4}\r".format(
                        schedule.activity_type_id.education_code,
                        schedule.level_id.education_code,
                        schedule.plan_id.education_code)
                multiple_lines = (
                    len(schedule.group_ids) > 1 and
                    (len(schedule.mapped("group_ids.course_id")) > 1 or
                     len(schedule.mapped("group_ids.course_id")) > 1))
                encode_string += schedule_string
                count = multiple_lines and (len(schedule.group_ids) - 1)
                for group in schedule.group_ids:
                    parent = group.parent_id or group
                    encode_string += "3{:0>8}{:0>4}{:0>4}{:<50}{:0>8}\r".format(
                        group.education_code,
                        timetable.attendance_id.daily_hour,
                        group.student_count,
                        group.description.replace("\n", " "),
                        parent.education_code)
                    if multiple_lines and count:
                        count -= 1
                        encode_string += schedule_string
            if schedule_msg:
                warning_msg += "<dl><dt>{}</dt>\n{}</dl>".format(
                    schedule.display_name, schedule_msg)
        for teacher in errored_teacher:
            warning_msg += _(
                "Teacher {} must have identification type and number."
                "<br/>\n").format(teacher.display_name)
        encode_string = encode_string.encode(HEZKUNTZA_ENCODING, "replace")
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
