# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Issue education",
    "version": "12.0.1.1.0",
    "license": "AGPL-3",
    "depends": [
        "education",
        "contacts_school",
        "calendar_school",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Customer Relationship Management",
    "data": [
        "security/ir.model.access.csv",
        "data/issue_education_data.xml",
        "views/calendar_event_view.xml",
        "views/res_partner_view.xml",
        "views/school_claim_view.xml",
        "views/school_issue_severity_scale_view.xml",
        "views/school_issue_type_view.xml",
        "views/school_college_issue_type_view.xml",
        "views/school_college_educational_measures_view.xml",
        "views/school_issue_site_view.xml",
        "views/school_issue_proof_view.xml",
        "views/school_issue_view.xml",
        "views/issue_education_menu_view.xml",
    ],
    "installable": True,
}
