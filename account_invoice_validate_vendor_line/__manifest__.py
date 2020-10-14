# Copyright 2020 Leire Martinez de Santos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice Validate Vendor Lines",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Tools",
    "depends": [
        "account",
        "account_payment_order",
        "base",
        "contacts_school",
        "contacts_school_education",
        "contract",
        "contract_payment_mode",
        "contract_school",
        "education",
    ],
    "data": [
        "views/account_invoice_line_view.xml",
        "views/account_invoice_view.xml",
    ],
    "installable": True,
}
