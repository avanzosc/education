# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import date, datetime, time


class FleetRoute(models.Model):
    _inherit = "fleet.route"

    request_dates = fields.One2many(
        comodel_name='fleet.route.request.date',
        inverse_name='route_id')
    requests_active = fields.Boolean('Requests active', compute="_compute_requests_active")

    @api.onchange('request_dates')
    def _compute_requests_active(self):
        for record in self:
            record.is_request_active()

    def update_date_active(self):
        for record in self:
            record.request_dates._compute_is_dates_active()

    def is_request_active(self):
        self.ensure_one()
        self.requests_active = True if True in self.request_dates.mapped('is_dates_active') else False

    @api.model
    def cron_update_date_active(self):
        for record in self:
            record.update_date_active()


class FleetRouteRequestDate(models.Model):
    _name = "fleet.route.request.date"
    _description = 'Route request inscription dates'
    _sql_constraints = [
        ('year_uniq', 'unique(route_id, academic_year_id)', 'Route and Academic year combination is not Unique!'),
    ]
    route_id = fields.Many2one(
        comodel_name="fleet.route", string="Route", help="Apply to routes", required=True)
    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        string="Academic year", required=True)
    date_init = fields.Datetime("Date Init")
    date_end = fields.Datetime("Date End")
    date_init_passenger = fields.Date("Date Init Passenger")
    date_end_passenger = fields.Date("Date End Passenger")
    is_dates_active = fields.Boolean('Date active', compute="_compute_is_dates_active")

    def _compute_is_dates_active(self):
        for record in self:
            today = datetime.today()
            record.is_dates_active = (not record.date_init or record.date_init <= today) and (not record.date_end or record.date_end >= today)

    def onchange_dates(self):
        self._compute_is_dates_active()

    @api.model
    def create(self, vals):
        res = super(FleetRouteRequestDate, self).create(vals)
        res._compute_is_dates_active()
        return res


class FleetRouteRequest(models.Model):
    _name = "fleet.route.request"
    _description = 'Stop areas for fleet routes'

    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        string="Academic year")
    request_date = fields.Many2one(
        comodel_name="fleet.route.request.date",
        string="Request date")
    education_center_id = fields.Many2one(
        comodel_name='res.partner',
        string='Education Center',
        domain="[('educational_category', '=', 'school')]",
    )
    date = fields.Datetime("Date")
    date_init = fields.Date("Date Init")
    date_end = fields.Date("Date End")
    parent_id = fields.Many2one(
        comodel_name='res.partner',
        string='Parent',
    )
    student_id = fields.Many2one(
        comodel_name='res.partner',
        string='Student',
    )
    departure_area_id = fields.Many2one(
        comodel_name='fleet.route.area',
        string='Depatrure area',
    )

    departure_stop_id = fields.Many2one(
        comodel_name='fleet.route.stop',
        string='Departure stop',
    )

    return_area_id = fields.Many2one(
        comodel_name='fleet.route.area',
        string='Return area',
    )

    return_stop_id = fields.Many2one(
        comodel_name='fleet.route.stop',
        string='Return stop',
    )

    passenger_ids = fields.Many2many(
        comodel_name='fleet.route.stop.passenger',
        string='Passengers',
        relation='rel_request_passenger',
        column1='request_id', column2='passenger_id'
    )
    dayofweek_ids = fields.Many2many(
        comodel_name="fleet.route.stop.weekday", string="Days of Week",
        relation="res_fleet_route_stop_request_weekday",
        column1="request_id", column2="weekday_id")

    state = fields.Selection(
        [
            ('open', 'Draft'),
            ('done', 'Accepted'),
            ('cancel', 'Cancelled'),
        ],
        string="Status", default='open',)

    def action_create_passengers(self):
        for record in self.filtered(lambda r: r.state == 'open'):
            values = {
                'partner_id': record.student_id.id,
                'start_date': record.date_init,
                'end_date': record.date_end,
            }
            if record.departure_stop_id:
                values.update({
                    'stop_id': record.departure_stop_id.id,
                })
                departure_passenger = self.env['fleet.route.stop.passenger'].create(values)
                record.passenger_ids = [(4, departure_passenger.id)]
            if record.return_stop_id:
                values.update({
                    'stop_id': record.return_stop_id.id,
                })
                return_passenger = self.env['fleet.route.stop.passenger'].create(values)
                record.passenger_ids = [(4, return_passenger.id)]
            record.state = 'done'

    def action_cancel_request(self):
        for record in self:
            record.state = 'cancel'

    def create(self, vals):
        if not vals.get('return_area_id', None):
            return_stop = self.env['fleet.route.stop'].browse(vals.get('return_stop_id'))
            vals.update({
                'return_area_id': return_stop.area_id.id if return_stop.area_id else None
            })
        if not vals.get('departure_area_id', None):
            departure_stop = self.env['fleet.route.stop'].browse(vals.get('departure_stop_id'))
            vals.update({
                'departure_area_id': departure_stop.area_id.id if departure_stop.area_id else None
            })
        res = super().create(vals)
        if not res.education_center_id:
            res.education_center_id = res.student_id.current_center_id.id
        if not res.academic_year_id and res.request_date:
            res.academic_year_id = res.request_date.academic_year_id.id
        if res.academic_year_id and not res.request_date:
            route = res.departure_stop_id.route_id if res.departure_stop_id else res.return_stop_id.route_id
            if route:
                request_date = route.request_dates.filtered(
                    lambda r: r.academic_year_id.id == res.academic_year_id.id)
                res.request_date = request_date.id if request_date else None
                if request_date:
                    res.date_init = res.request_date.date_init_passenger
                    res.date_end = res.request_date.date_end_passenger
        return
