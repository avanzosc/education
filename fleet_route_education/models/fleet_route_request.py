# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FleetRoute(models.Model):
    _inherit = "fleet.route"

    date_start_request = fields.Datetime("Date start requests")
    date_end_request = fields.Datetime("Date end requests")


class FleetRouteRequest(models.Model):
    _name = "fleet.route.request"
    _description = 'Stop areas for fleet routes'

    academic_year_id = fields.Many2one(
        comodel_name="education.academic_year",
        string="Academic year")
    education_center_id = fields.Many2one(
        comodel_name='res.partner',
        string='Education Center',
        domain="[('educational_category', '=', 'school')]",
    )
    date = fields.Datetime("Date")
    date_init = fields.Datetime("Date Init", related="departure_stop_id.route_id.date_start_request")
    date_end = fields.Datetime("Date End", related="departure_stop_id.route_id.date_end_request")
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
            values.update({
                'stop_id': record.departure_stop_id.id,
            })
            departure_passenger = self.env['fleet.route.stop.passenger'].create(values)
            values.update({
                'stop_id': record.return_stop_id.id,
            })
            return_passenger = self.env['fleet.route.stop.passenger'].create(values)
            record.passenger_ids = [(4, departure_passenger.id)]
            record.passenger_ids = [(4, return_passenger.id)]
            record.state = 'done'

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
        return
