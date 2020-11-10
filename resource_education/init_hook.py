# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


def post_init_hook(cr, registry):
    cr.execute(
        """
        UPDATE education_schedule_timetable t
        SET session_number = (
            SELECT daily_hour FROM resource_calendar_attendance a
            WHERE a.id = t.attendance_id);
        """)
