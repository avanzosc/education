# Copyright 2023 Leire Martinez de Santos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo import exceptions
from odoo.exceptions import UserError


class EducationNotebookLine(models.Model):
    _inherit = 'education.notebook.line'
    
    def get_survey_url(self):
        for record in self:
            if record.survey_id and record.competence_id.eval_mode == 'rubric':
                url_get = record.button_open_all_survey_inputs()
                return url_get.get('url', None)
