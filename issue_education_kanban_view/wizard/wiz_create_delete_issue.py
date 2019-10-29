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
    issue_type = fields.Integer(string='Issue type')

    @api.model
    def default_get(self, var_fields):
        res = super(WizCreateDeleteIssue, self).default_get(var_fields)
        student = self.env['res.partner'].browse(
            self.env.context.get('active_id'))
        res.update({'student_id': student.id,
                    'issue_type': self.env.context.get('issue_type')})
        schedule = False
        if self.env.context.get('education_schedule', False):
            schedule = self.env['education.schedule'].browse(
                self.env.context.get('education_schedule'))
            res['schedule_id'] = schedule.id
        issue, school_issue_type = self._find_issue(
            self.env.context.get('issue_type'), schedule, student)
        if issue:
            res.update({'name': _('You are going to DELETE an issue')})
        else:
            res.update({'name': _('You are going to CREATE an issue')})
        return res

    @api.multi
    def _find_issue(self, issue_type_id, schedule, student):
        issue_obj = self.env['school.issue']
        type_obj = self.env['school.college.issue.type']
        today = fields.Date.from_string(fields.Date.today())
        # cond = [('sequence', '=', issue_type)]
        # if schedule:
        #     cond.append(('school_id', '=', schedule.center_id.id))
        # else:
        #     cond.append(('school_id', '=',
        #                  student.current_center_id.id))
        school_issue_type = type_obj.browse(issue_type_id)
        cond = [('student_id', '=', student.id),
                ('school_issue_type_id', '=', issue_type_id),
                ('issue_date', '=', today)]
        if schedule:
            cond.append(('education_schedule_id', '=',  schedule.id))
        else:
            cond.append(('education_schedule_id', '=',  False))
        issue = issue_obj.search(cond, limit=1)
        return issue, school_issue_type

    @api.multi
    def create_delete_issue(self):
        issue_obj = self.env['school.issue']
        issue, school_issue_type = self._find_issue(
            self.issue_type, self.schedule_id, self.student_id)
        if issue:
            issue.unlink()
        else:
            vals = self.prepare_vals_for_create_issue(school_issue_type)
            issue = issue_obj.create(vals)
            if issue.issue_type_id.generate_part:
                issue._generate_part()
        # Close wizard and reload view
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }

    def prepare_vals_for_create_issue(self, school_issue_type):
        today = fields.Date.from_string(fields.Date.today())
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
            'site_id': school_issue_type.issue_type_id.site_id.id,
        }
        return vals
