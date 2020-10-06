# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        UPDATE
            education_schedule_timetable tt
        SET
            session_number = (
                SELECT daily_hour
                FROM   resource_calendar_attendance ca
                WHERE  ca.id = tt.attendance_id);
    """)
