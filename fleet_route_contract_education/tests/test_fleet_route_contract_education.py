# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import FleetRouteContractEducationCommon
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestFleetRouteContractEducation(FleetRouteContractEducationCommon):

    def test_contract_line_wizard(self):
        contract_domain = [
            ("child_id", "=", self.student.id),
            ("academic_year_id", "=", self.next_academic_year.id),
        ]
        self.assertFalse(self.contract_model.search(contract_domain))
        self.assertFalse(self.student.additional_product_ids)
        passengers = self.passenger_report.search([
            ("student_id", "=", self.student.id)])
        wizard = self.wizard_model.with_context(
            active_model="res.partner.fleet.route.report",
            active_ids=passengers.ids).create({
                "product_id": self.recurrent_product.id,
                "unit_price": self.recurrent_product.lst_price,
                "date_start": self.next_academic_year.date_start,
                "date_end": self.next_academic_year.date_end,
            })
        self.assertTrue(wizard.student_ids)
        wizard.button_create_contract_line()
        self.assertTrue(self.contract_model.search(contract_domain))
        self.assertIn(
            self.recurrent_product, self.student.additional_product_ids)
