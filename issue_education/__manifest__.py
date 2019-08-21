# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Issue education",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "education",
        "contacts_school",
        "crm_claim"
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Customer Relationship Management",
    "data": [
        "security/ir.model.access.csv",
        "views/school_issue_type_master_view.xml",
        "views/school_issue_severity_level_view.xml",
        "views/school_issue_type_view.xml",
        "views/school_college_issue_type_view.xml",
        "views/school_college_educational_measures_view.xml",
        "views/school_issue_site_view.xml",
        "views/school_issue_proof_view.xml",
        "views/school_issue_view.xml",
    ],
    "installable": True,
}