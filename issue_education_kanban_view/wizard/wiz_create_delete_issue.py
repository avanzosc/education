# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


class WizCreateDeleteIssue(models.TransientModel):
    _name = "wiz.create.delete.issue"
    _description = "Wizard for create or delete issue on day"

    name = fields.Char(string='Description')
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner', required=True)
    schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule')
    group_id = fields.Many2one(
        string='Group', comodel_name='education.group')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.college.issue.type')

    @api.model
    def default_get(self, var_fields):
        context = self.env.context
        res = super(WizCreateDeleteIssue, self).default_get(var_fields)
        student_id = context.get('active_id')
        issue_type_id = context.get('issue_type')
        group_id = context.get('education_group_id')
        schedule_id = context.get('education_schedule_id')
        if not group_id and schedule_id:
            schedule = self.env['education.schedule'].browse(schedule_id)
            group_id = schedule.group_ids.filtered(
                lambda g: student_id in g.student_ids.ids)[:1].id
        res.update({
            'student_id': student_id,
            'issue_type_id': issue_type_id,
            'schedule_id': schedule_id,
            'group_id': group_id,
        })
        issue = self._find_issue(
            student_id, issue_type_id, group_id, schedule_id)
        issue_type = self.env['school.college.issue.type'].browse(
            issue_type_id)
        if issue:
            res.update({
                'name': _('You are going to DELETE an {} issue').format(
                    issue_type.name.lower()),
            })
        else:
            res.update({
                'name': _('You are going to CREATE an {} issue').format(
                    issue_type.name.lower()),
            })
        return res

    @api.multi
    def _find_issue(self, student_id, issue_type_id, group_id, schedule_id):
        today = fields.Date.context_today(self)
        cond = [
            ('issue_date', '=', today),
            ('student_id', '=', student_id),
            ('school_issue_type_id', '=', issue_type_id),
            ('group_id', '=', group_id),
            ('education_schedule_id', '=', schedule_id)]
        return self.env['school.issue'].search(cond, limit=1)

    @api.multi
    def create_delete_issue(self):
        issue_obj = self.env['school.issue']
        issue = self._find_issue(
            self.student_id.id, self.issue_type_id.id, self.group_id.id,
            self.schedule_id.id)
        if issue:
            issue.unlink()
        else:
            vals = self.prepare_vals_for_create_issue(self.issue_type_id)
            issue_obj.create(vals)
        # Close wizard and reload view
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }

    def prepare_vals_for_create_issue(self, school_issue_type):
        today = fields.Date.context_today(self)
        name = self.env['school.issue'].create_issue_name(
            self.student_id, school_issue_type, self.schedule_id)
        vals = {
            'name': name,
            'school_id': school_issue_type.school_id.id,
            'school_issue_type_id': school_issue_type.id,
            'issue_type_id': school_issue_type.issue_type_id.id,
            'requires_justification':
            school_issue_type.issue_type_id.requires_justification,
            'affect_to': school_issue_type.issue_type_id.affect_to,
            'student_id': self.student_id.id,
            'reported_id': self.env.user.id,
            'issue_date': today,
            'education_schedule_id': self.schedule_id.id,
            'group_id': self.group_id.id,
            'site_id': school_issue_type.issue_type_id.site_id.id,
        }
        return vals
