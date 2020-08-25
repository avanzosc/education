# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs


class ResPartnerFleetRouteReport(models.Model):
    _name = "res.partner.fleet.route.report"
    _description = "Partner Route Stops Report"
    _auto = False
    _order = "center_id,level_id,course_id,student_id"

    student_id = fields.Many2one(
        comodel_name="res.partner", string="Passenger",
        domain="[('educational_category','=','student')]")
    center_id = fields.Many2one(
        comodel_name="res.partner", string="Education Center",
        domain="[('educational_category','=','school')]")
    level_id = fields.Many2one(
        comodel_name="education.level", string="Education Level")
    course_id = fields.Many2one(
        comodel_name="education.course", string="Education Course")
    bus_passenger = fields.Selection(
        selection=[("yes", "Yes"),
                   ("no", "No")], string="Uses Bus")
    going_stop_id = fields.Many2one(
        comodel_name="fleet.route.stop", string="Going Stop")
    coming_stop_id = fields.Many2one(
        comodel_name="fleet.route.stop", string="Coming Stop")

    def _select(self):
        select_str = """
            SELECT
                row_number() OVER () as id,
                stu.id AS student_id,
                stu.current_center_id AS center_id,
                stu.current_level_id AS level_id,
                stu.current_course_id AS course_id,
                stu.bus_passenger AS bus_passenger,
                (SELECT stop_id FROM fleet_route_stop_passenger
                 WHERE partner_id = stu.id
                  AND stop_id IN
                  (SELECT id FROM fleet_route_stop
                   WHERE route_id IN
                   (SELECT id FROM fleet_route WHERE direction = 'going'))
                 LIMIT 1) AS going_stop_id,
                (SELECT stop_id FROM fleet_route_stop_passenger
                 WHERE partner_id = stu.id
                  AND stop_id IN
                  (SELECT id FROM fleet_route_stop
                   WHERE route_id IN
                   (SELECT id FROM fleet_route WHERE direction = 'coming'))
                 LIMIT 1) AS coming_stop_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM res_partner AS stu
        """
        return from_str

    def _where(self):
        where_str = """
            WHERE stu.educational_category = 'student'
        """
        return where_str

    def _group_by(self):
        group_by_str = """
                GROUP BY stu.id, stu.current_center_id,
                stu.current_level_id, stu.current_course_id, stu.bus_passenger
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = res_partner_fleet_route_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as
                (
                %s %s %s %s
            )""", (
                AsIs(self._table), AsIs(self._select()), AsIs(self._from()),
                AsIs(self._where()), AsIs(self._group_by()),))
