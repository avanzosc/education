# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval
from datetime import timedelta


class SchoolClaim(models.Model):
    _name = 'school.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Issue Report'

    school_issue_id = fields.Many2one(
        string='Issue', comodel_name='school.issue')
    school_id = fields.Many2one(
        comodel_name='res.partner',
        string='Education Center',
        domain="[('educational_category', '=', 'school')]",
        required=True)
    school_issue_ids = fields.One2many(
        comodel_name='school.issue', string='Issues', inverse_name='claim_id')
    school_issue_count = fields.Integer(
        string='Issue Count', compute='_compute_issue_count')
    name = fields.Char(string='Description', required=True)
    issue_date = fields.Date(string='Date', required=True)
    school_issue_type_id = fields.Many2one(
        string='School issue type', comodel_name='school.college.issue.type',
        required=True)
    education_schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule')
    education_group_id = fields.Many2one(
        string='Education Group', comodel_name='education.group')
    reported_id = fields.Many2one(
        string='Reported by', comodel_name='res.users', required=True)
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner')
    description_facts = fields.Text(string='Description of the facts')
    sanction_specification = fields.Text(string='Sanction specification')
    educational_measure_ids = fields.Many2many(
        string="Educational measures",
        comodel_name='school.college.educational.measure',
        relation='rel_school_claims_educational_measures',
        column1='school_claim_id', column2='educational_measure_id',
        compute='_compute_educational_measure_ids', store=True)
    educational_measure_concretion = fields.Text(
        string='Educational measure concretion')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('notified', 'Notified'),
        ('confirmed', 'Educational measure confirmed'),
        ('fulfill', 'Sanction fulfill'),
        ('closed', 'Closed'),
        ], string='Status', copy=False, index=True, default='draft',
        track_visibility='onchange')
    calendar_event_count = fields.Integer(
        string='Meetings Count', compute='_compute_calendar_events')

    @api.depends('school_issue_type_id',
                 'school_issue_type_id.educational_measure_ids')
    def _compute_educational_measure_ids(self):
        for claim in self.filtered(lambda c: c.school_issue_type_id):
            claim.educational_measure_ids = [
                (6, 0, claim.mapped(
                    'school_issue_type_id.educational_measure_ids').ids)]

    @api.multi
    def _compute_calendar_events(self):
        meeting_obj = self.env['calendar.event']
        res_model_id = self.env['ir.model']._get_id(self._name)
        for claim in self:
            claim.calendar_event_count = meeting_obj.search_count([
                ('res_id', '=', claim.id),
                ('res_model_id', '=', res_model_id),
            ])

    @api.model
    def create(self, values):
        claim = super(SchoolClaim, self).create(values)
        if claim.school_issue_type_id.notify_ids:
            claim.message_subscribe(
                list(claim.mapped('school_issue_type_id.notify_ids').ids))
        return claim

    @api.multi
    def open_calendar_event(self):
        action = self.env.ref('calendar.action_calendar_event')
        action_dict = action.read()[0] if action else {}
        res_model_id = self.env['ir.model']._get_id(self._name)
        domain = expression.AND([
            [('res_id', '=', self.id),
             ('res_model_id', '=', res_model_id)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict

    @api.multi
    def button_notified(self):
        self.ensure_one()
        gravity_scale = (
            self.school_issue_type_id.issue_type_id.gravity_scale_id)
        if int(gravity_scale.gravity_scale) <= 0:
            self.create_calendar_event()
        self.state = 'notified'

    @api.multi
    def button_confirmed(self):
        self.state = 'confirmed'

    @api.multi
    def button_fulfill(self):
        self.state = 'fulfill'

    @api.multi
    def button_closed(self):
        self.state = 'closed'

    def create_calendar_event(self):
        families = set(self.student_id.mapped(
            'child2_ids.family_id'))
        for family in families:
            lines = self.student_id.mapped(
                'child2_ids').filtered(
                lambda c: c.family_id.id == family.id)
            responsibles = set(lines.mapped('responsible_id'))
            progenitors = self.env['res.partner']
            for p in responsibles:
                progenitors += p
            if progenitors:
                self._create_calendar_event_for_progenitor(family, progenitors)

    def _create_calendar_event_for_progenitor(self, family, progenitors):
        self.ensure_one()
        vals = self._catch_values_for_progenitor(family, progenitors)
        vals.update({
            'res_id': self.id,
            'res_model': self._name,
            'res_model_id': self.env['ir.model']._get_id(self._name),
        })
        self.env['calendar.event'].create(vals)

    def _catch_values_for_progenitor(self, family, progenitors):
        today = fields.Datetime.context_timestamp(
            self, fields.Datetime.today())
        label = self.env.ref(
            'issue_education.calendar_event_type_disciplinary')
        alarm = self.env.ref('calendar.alarm_notif_1')
        start = today.replace(hour=15) - today.utcoffset()
        stop = start + timedelta(minutes=30)
        progenitors |= self.reported_id.partner_id
        vals = {
            'name': self.name,
            'allday': False,
            'start': fields.Datetime.to_string(start),
            'stop': fields.Datetime.to_string(stop),
            'user_id': self.reported_id.id,
            'family_id': family.id,
            'student_id': self.student_id.id,
            'teacher_id': self.education_schedule_id.teacher_id.id,
            'alarm_ids': [(6, 0, alarm.ids)],
            'partner_ids': [(6, 0, progenitors.ids)],
            'categ_ids': [(6, 0, label.ids)],
        }
        return vals
