# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


class WizCreateDeleteIssue(models.TransientModel):
    _name = "wiz.create.delete.issue"
    _description = "Wizard for create or delete issue on day"

    name = fields.Char(string='Description')
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner')
    schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule')
    group_id = fields.Many2one(
        string='Group', comodel_name='education.group')
    issue_type_id = fields.Many2one(
        string='Issue type', comodel_name='school.college.issue.type')
    create_issue = fields.Boolean(compute='_compute_create')

    @api.model
    def default_get(self, var_fields):
        context = self.env.context
        res = super(WizCreateDeleteIssue, self).default_get(var_fields)
        student_id = context.get('active_id')
        issue_type_id = context.get('issue_type')
        group_id = context.get('education_group_id')
        scheduled_id = context.get('education_schedule_id')
        if not group_id and scheduled_id:
            schedule = self.env['education.schedule'].browse(scheduled_id)
            group_id = schedule.group_ids.filtered(
                lambda g: student_id in g.student_ids.ids)[:1].id
        res.update({
            'student_id': student_id,
            'issue_type_id': issue_type_id,
            'schedule_id': scheduled_id,
            'group_id': group_id,
        })
        issue = self._find_issue(
            student_id, issue_type_id, group_id, scheduled_id)
        if issue:
            res.update({'name': _('You are going to DELETE an issue')})
        else:
            res.update({'name': _('You are going to CREATE an issue')})
        return res

    @api.multi
    @api.depends('student_id', 'issue_type_id', 'group_id', 'schedule_id')
    def _compute_create(self):
        for wiz in self:
            wiz.create_issue = bool(wiz._find_issue(
                wiz.student_id.id, wiz.issue_type_id.id, wiz.group_id.id,
                wiz.schedule_id.id))

    @api.multi
    def _find_issue(self, student_id, issue_type_id, group_id, schedule_id):
        issue_obj = self.env['school.issue']
        # type_obj = self.env['school.college.issue.type']
        today = fields.Date.context_today(self)
        # school_issue_type = type_obj.browse(issue_type_id)
        cond = [
            ('issue_date', '=', today),
            ('student_id', '=', student_id),
            ('school_issue_type_id', '=', issue_type_id),
            ('group_id', '=', group_id),
            ('education_schedule_id', '=', schedule_id)]
        # if schedule:
        #     cond.append(('education_schedule_id', '=',  schedule.id))
        # else:
        #     cond.append(('education_schedule_id', '=',  False))
        issue = issue_obj.search(cond, limit=1)
        return issue  # , school_issue_type

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
        today = fields.Date.from_string(fields.Date.context_today(self))
        name = _('School: {}, Issue type: {}').format(
            self.student_id.current_center_id.name,
            school_issue_type.name)
        if self.schedule_id:
            name = _('School: {}, Education subject: {}, Session: {}').format(
                self.schedule_id.center_id.name,
                self.schedule_id.subject_id.description,
                self.schedule_id.session_number)
        vals = {
            'name': name,
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
