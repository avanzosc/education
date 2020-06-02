# Copyright 2020 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    photo_header_email = fields.Binary(
        string='Photo header email', attachment=True)
    twitter_icon = fields.Binary(
        string='Twitter icon', attachment=True)
    twitter_user = fields.Char(
        string='Twitter user')
    facebook_icon = fields.Binary(
        string='Facebook icon', attachment=True)
    facebook_user = fields.Char(
        string='Facebook user')
    link1_icon = fields.Binary(
        string='Link 1 icon', attachment=True)
    link1_text = fields.Char(
        string='Link 1 text')
    link2_icon = fields.Binary(
        string='Link 2 icon', attachment=True)
    link2_text = fields.Char(
        string='Link 2 text')
    link3_icon = fields.Binary(
        string='Link 3 icon', attachment=True)
    link3_text = fields.Char(
        string='Link 3 text')
    footer_text = fields.Text(
        string='Footer text', translate=True)
