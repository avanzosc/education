# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        UPDATE education_schedule_timetable t
        SET attendance_id = (
            SELECT id
            FROM resource_calendar_attendance a
            WHERE t.calendar_id = a.calendar_id
            AND t.dayofweek = a.dayofweek
            AND t.hour_from = a.hour_from
            AND t.hour_to = a.hour_to);
    """)
