# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class WizCreateAssistanceIssue(models.TransientModel):
    _name = "wiz.create.assistance.issue"
    _description = "Wizard for assistance issue creation"

    @api.model
    def _get_selection_dayofweek(self):
        return self.env["resource.calendar.attendance"].fields_get(
            allfields=["dayofweek"])["dayofweek"]["selection"]

    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Students",
    )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )
    dayofweek = fields.Selection(
        selection="_get_selection_dayofweek",
        string="Day of Week",
        compute="_compute_dayofweek",
    )

    @api.model
    def default_get(self, fields):
        result = super(WizCreateAssistanceIssue, self).default_get(fields)
        if self.env.context.get("active_ids"):
            result.update({
                "partner_ids": [
                    (6, 0, self.env.context.get("active_ids"))],
            })
        return result

    @api.depends("date")
    def _compute_dayofweek(self):
        for record in self:
            record.dayofweek = str(record.date.weekday())

    @api.multi
    def create_assistance_issues(self):
        assistance_type = self.env.ref("issue_education.assistance_issue_type_master")
        assistance_school_types = self.env["school.college.issue.type"].search([
            ("issue_type_id", "=", assistance_type.id),
        ])
        issue_obj = issues = self.env["school.issue"]
        academic_year = self.env["education.academic_year"].search([
            ("date_start", "<=", self.date),
            ("date_end", ">=", self.date),
        ])
        for partner in self.partner_ids:
            for group in partner.student_group_ids.filtered(
                    lambda g: g.academic_year_id == academic_year):
                assistance_school_type = assistance_school_types.filtered(
                    lambda t: t.school_id == group.center_id and
                    t.education_level_id == group.level_id)
                for schedule in group.schedule_ids.filtered(
                        lambda s: not s.timetable_ids or
                        self.dayofweek in s.mapped("timetable_ids.dayofweek")):
                    group = schedule.group_ids.filtered(
                        lambda g: partner in g.student_ids)[:1]
                    issue = issue_obj._find_issue(
                        partner.id, self.date, assistance_school_type[:1].id,
                        group.id, schedule.id)
                    if not issue:
                        issue_vals = issue_obj.prepare_issue_vals(
                            self.date, assistance_school_type[:1], partner,
                            schedule, group)
                        issue = issue_obj.create(issue_vals)
                    issues |= issue
        action = self.env.ref("issue_education.action_school_issue")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("id", "in", issues.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
