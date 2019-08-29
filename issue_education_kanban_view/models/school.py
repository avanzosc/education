# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from pytz import timezone, utc


class SchoolClaims(models.Model):
    _name = 'school.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'School claims'

    school_issue_id = fields.Many2one(
        string='Issue', comodel_name='school.issue')
    name = fields.Char(
        string='Description', related='school_issue_id.name', store=True)
    issue_date = fields.Date(
        string='Date', related='school_issue_id.issue_date', store=True)
    school_issue_type_id = fields.Many2one(
        string='School issue type', comodel_name='school.college.issue.type',
        related='school_issue_id.school_issue_type_id', store=True)
    education_schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule',
        related='school_issue_id.education_schedule_id', store=True)
    reported_id = fields.Many2one(
        string='Reported by', comodel_name='res.users',
        related='school_issue_id.reported_id', store=True)
    student_id = fields.Many2one(
        string='Student', comodel_name='res.partner',
        related='school_issue_id.student_id', store=True)
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
    state = fields.Selection([
        ('draft', _('Quotation')),
        ('notified', _('Notified')),
        ('confirmed', _('Educational measure confirmed')),
        ('fulfill', _('Sanction fulfill')),
        ('closed', _('Closed')),
        ], string='Status', copy=False, index=True, default='draft',
        track_visibility='onchange')

    @api.depends('school_issue_type_id',
                 'school_issue_type_id.educational_measure_ids')
    def _compute_educational_measure_ids(self):
        for claim in self.filtered(lambda c: c.school_issue_type_id):
            claim.educational_measure_ids = [
                (6, 0, claim.school_issue_type_id.educational_measure_ids.ids)]

    @api.multi
    def button_notified(self):
        gravity_scale = (
            self.school_issue_type_id.issue_type_id.gravity_scale_id)
        if gravity_scale.gravity_scale in ('0', '-1', '-2', '-3', '-4'):
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
                'child2_ids').filtered(lambda c: c.family_id.id ==
                                       family.id)
            responsibles = set(lines.mapped('responsible_id'))
            progenitors = self.env['res.partner']
            for p in responsibles:
                progenitors += p
            if progenitors:
                self._create_calendar_event_for_progenitor(family, progenitors)

    def _create_calendar_event_for_progenitor(self, family, progenitors):
        vals = self._catch_values_for_progenitor(family, progenitors)
        self.env['calendar.event'].create(vals)

    def _catch_values_for_progenitor(self, family, progenitors):
        day = fields.Date.to_string(fields.Date.context_today(self))
        label = self.env.ref(
            'issue_education_kanban_view.calendar_event_type_disciplinary')
        alarm = self.env.ref('calendar.alarm_notif_1')
        start = self._convert_to_utc_date(
            "{} {}".format(day, '15:00:00'), tz=self.env.user.tz)
        stop = self._convert_to_utc_date(
            "{} {}".format(day, '15:30:00'), tz=self.env.user.tz)
        partners = self.reported_id.partner_id.ids + progenitors.ids
        vals = {
            'name': self.name,
            'allday': False,
            'start': start,
            'stop': stop,
            'duration': 0.50,
            'user_id': self.reported_id.id,
            'family_id': family.id,
            'alarm_ids': [(6, 0, [alarm.id])],
            'partner_ids': [(6, 0, partners)],
            'categ_ids': [(6, 0, [label.id])]}
        return vals

    def _convert_to_utc_date(self, date, tz=u'UTC'):
        if not date:
            return False
        if not tz:
            tz = u'UTC'
        date = fields.Datetime.from_string(date)
        local = timezone(tz)
        local_date = local.localize(date, is_dst=None)
        utc_date = local_date.astimezone(utc).replace(tzinfo=None)
        return utc_date


class SchoolIssue(models.Model):
    _inherit = 'school.issue'

    education_schedule_id = fields.Many2one(
        string='Schedule', comodel_name='education.schedule')
    claim_id = fields.Many2one(
        string='Claim', comodel_name='school.claim')

    def _generate_part(self):
        vals = self._cath_values_for_generate_part()
        part = self.env['school.claim']. create(vals)
        self.claim_id = part.id

        return part

    def _cath_values_for_generate_part(self):
        vals = {'school_issue_id': self.id}
        if self.school_issue_type_id.notify_ids:
            followers = []
            for notify in self.school_issue_type_id.notify_ids:
                followers.append((0, 0, {'res_model': 'school.claim',
                                         'partner_id': notify.id}))
            vals['message_follower_ids'] = followers
        return vals
