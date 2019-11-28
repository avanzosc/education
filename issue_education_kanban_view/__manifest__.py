# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Issue Education Kanban View",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "calendar_school",
        "crm_claim",
        "issue_education",
        "web_one2many_kanban",
        "web_ir_actions_act_multi",
        "web_ir_actions_act_view_reload",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Customer Relationship Management",
    "data": [
        "security/ir.model.access.csv",
        "wizard/wiz_create_delete_issue_view.xml",
        "wizard/wiz_create_issue_view.xml",
        "views/education_group_view.xml",
        "views/education_schedule_view.xml",
        "views/school_issue_view.xml",
        "views/res_partner_view.xml",
        "views/issue_education_kanban_view_menu.xml",
    ],
    "installable": True,
}
