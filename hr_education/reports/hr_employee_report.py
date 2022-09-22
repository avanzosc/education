# Copyright 2020 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo import api, fields, models
from psycopg2.extensions import AsIs


class HrEmployeeReport(models.Model):
    _name = 'hr.employee.report'
    _description = 'Employee Report'
    _auto = False
    _rec_name = 'employee_id'
    _order = "employee_id,birthday"

    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee")
    # private partner
    address_home_id = fields.Many2one(
        'res.partner', 'Private Address')
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status')
    place_of_birth = fields.Char(string='Place of Birth')
    country_of_birth = fields.Many2one(
        comodel_name='res.country', string="Country of Birth")
    birthday = fields.Date('Date of Birth')
    ssnid = fields.Char('SSN No', help='Social Security Number')
    sinid = fields.Char('SIN No', help='Social Insurance Number')
    identification_id = fields.Char(string='Identification No')
    passport_id = fields.Char('Passport No')
    permit_no = fields.Char('Work Permit No')
    visa_no = fields.Char('Visa No')
    visa_expire = fields.Date('Visa Expire Date')
    emergency_contact = fields.Char("Emergency Contact")
    emergency_phone = fields.Char("Emergency Phone")
    km_home_work = fields.Integer(string="Km home-work")

    # work
    address_id = fields.Many2one(
        comodel_name='res.partner', string='Work Address')
    work_phone = fields.Char(string='Work Phone')
    mobile_phone = fields.Char(string='Work Mobile')
    work_email = fields.Char(string='Work Email')
    work_location = fields.Char(string='Work Location')
    # employee in company
    job_id = fields.Many2one(comodel_name='hr.job', string='Job Position')
    department_id = fields.Many2one(
        comodel_name='hr.department', string='Department')
    parent_id = fields.Many2one(comodel_name='hr.employee', string='Manager')
    coach_id = fields.Many2one(comodel_name='hr.employee', string='Coach')
    edu_idtype_id = fields.Many2one(
        comodel_name="education.idtype", string="ID Type")
    edu_type_id = fields.Many2one(
        comodel_name="hr.employee.edu_type", string="Employee Education Type")
    active = fields.Boolean()

    def _select(self):
        select_str = """
            SELECT
                row_number() OVER () as id,
                e.id AS employee_id,
                e.active AS active,
                e.address_home_id AS address_home_id,
                e.country_id AS country_id,
                e.gender AS gender,
                e.marital AS marital,
                e.place_of_birth AS place_of_birth,
                e.country_of_birth AS country_of_birth,
                e.birthday AS birthday,
                e.ssnid AS ssnid,
                e.sinid AS sinid,
                e.identification_id AS identification_id,
                e.passport_id AS passport_id,
                e.permit_no AS permit_no,
                e.visa_no AS visa_no,
                e.visa_expire AS visa_expire,
                e.emergency_contact AS emergency_contact,
                e.emergency_phone AS emergency_phone,
                e.km_home_work AS km_home_work,
                e.address_id AS address_id,
                e.work_phone AS work_phone,
                e.mobile_phone AS mobile_phone,
                e.work_email AS work_email,
                e.work_location AS work_location,
                e.job_id AS job_id,
                e.department_id AS department_id,
                e.parent_id AS parent_id,
                e.coach_id AS coach_id,
                e.edu_idtype_id AS edu_idtype_id,
                e.edu_type_id AS edu_type_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM hr_employee e
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY e.id, e.address_home_id, e.country_id, e.gender,
                e.marital, e.place_of_birth, e.country_of_birth, e.birthday,
                e.ssnid, e.sinid, e.identification_id, e.passport_id,
                e.permit_no, e.visa_no, e.visa_expire, e.emergency_contact,
                e.emergency_phone, e.km_home_work, e.address_id, e.work_phone,
                e.mobile_phone, e.work_email, e.work_location, e.job_id,
                e.department_id, e.parent_id, e.coach_id, e.edu_idtype_id,
                e.edu_type_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as
                (
                %s %s %s
            )""", (
                AsIs(self._table), AsIs(self._select()), AsIs(self._from()),
                AsIs(self._group_by()),))
