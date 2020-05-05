# Copyright 2020 Daniel Campos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_course_ids = fields.Many2many(
        string='Available Courses', comodel_name='education.course',
        relation='rel_product_education_course', column1='product_tmpl_id',
        column2='course_id')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_extracurricular = fields.Boolean(string='Extracurricular')
