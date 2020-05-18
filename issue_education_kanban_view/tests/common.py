# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.issue_education.tests.common import TestIssueEducationCommon


class TestIssueEducationKanbanCommon(TestIssueEducationCommon):

    @classmethod
    def setUpClass(cls):
        super(TestIssueEducationKanbanCommon, cls).setUpClass()
        cls.wiz_create_delete_model = cls.env['wiz.create.delete.issue']
        cls.wiz_create_model = cls.env['wiz.create.issue']
        cls.classroom = cls.env.ref(
            'issue_education.classroom_school_issue_site')
        current_year = cls.env['education.academic_year'].search([
            ('current', '=', True)])
        if not current_year:
            start = cls.today.replace(month=1, day=1)
            end = cls.today.replace(month=12, day=31)
            cls.academic_year.write({
                'date_start': start,
                'date_end': end,
            })
        else:
            cls.group.write({
                'academic_year_id': current_year.id,
            })
            cls.schedule.write({
                'academic_year_id': current_year.id,
            })
