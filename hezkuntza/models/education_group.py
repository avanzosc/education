# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from lxml import etree
import base64
import logging

logger = logging.getLogger(__name__)


class EducationGroup(models.Model):
    _inherit = "education.group"

    education_code = fields.Char(default="/", readonly=True)

    @api.model
    def create(self, values):
        group_codes = self.search([
            ("center_id", "=", values.get("center_id")),
            ("academic_year_id", "=", values.get("academic_year_id")),
        ], order="education_code DESC").mapped("education_code")
        codes = [int(code) if code.isdigit() else 0 for code in group_codes]
        if values.get("education_code", "/") == "/":
            code_num = max(codes) + 1 if codes else 1
            values["education_code"] = str(code_num).rjust(8, "0")
        return super(EducationGroup, self).create(values)

    @api.multi
    def get_xsd_file_path(self):
        self.ensure_one()
        return "hezkuntza/data/XSD_historialv4.xsd"

    @api.multi
    def generate_xml_file(self):
        self.ensure_one()
        xsd_file = self.get_xsd_file_path()
        gen_args = {
            # 'bic_xml_tag': bic_xml_tag,
            # 'name_maxsize': name_maxsize,
            # 'convert_to_ascii': pay_method.convert_to_ascii,
            'payment_method': 'DD',
            'file_prefix': 'sdd_',
            # 'pain_flavor': pain_flavor,
            'xsd_file': xsd_file,
        }
        xml_root = etree.Element("DatosHistoriales")
        CodigoCentroJuridico = etree.SubElement(
            xml_root, "CodigoCentroJuridico")
        CodigoCentroJuridico.text = self.center_id.education_code

        level_code = self.level_id.hezkuntza_level
        if level_code == "1120":
            level1 = "Primaria"
            level2 = "CursosPrimaria"
            level3 = "CursoPrimaria"
        elif level_code == "2260":
            level1 = "Secundaria"
            level2 = "CursosSecundaria"
            level3 = "CursoSecundaria"

        elif level_code == "3270":
            level1 = "Bachillerato"
            level2 = "CursosBachillerato"
            level3 = "CursoBachillerato"
        else:
            level1 = "FP"
            level2 = "CiclosFormativos"
            level3 = "CicloFormativo"

        for student in self.student_ids:
            Historial = etree.SubElement(xml_root, "Historial")
            DatosComunes = etree.SubElement(Historial, "DatosComunes")
            NivelEducativo = etree.SubElement(DatosComunes, "NivelEducativo")
            CodigoNivelEducativo = etree.SubElement(NivelEducativo, "CodigoNivelEducativo")
            CodigoNivelEducativo.text = level_code

            IdentificacionAlumno = etree.SubElement(DatosComunes, "IdentificacionAlumno")
            CodigoCentro = etree.SubElement(IdentificacionAlumno, "CodigoCentro")
            CodigoAlumno = etree.SubElement(CodigoCentro, "CodigoAlumno")
            CodigoAlumno.text = student.education_code

            Level1 = etree.SubElement(Historial, level1)
            Level2 = etree.SubElement(Level1, level2)
            Level3 = etree.SubElement(Level2, level3)

            Centro = etree.SubElement(Level3, "Centro")
            CodigoCentroJuridico = etree.SubElement(
                Centro, "CodigoCentroJuridico")
            CodigoCentroJuridico.text = self.center_id.education_code
            # ValorCurso = etree.SubElement(Level3, "ValorCurso")
            AnoAcademicoInicio = etree.SubElement(Level3, "AnoAcademicoInicio")
            AnoAcademicoInicio.text = str(self.academic_year_id.date_start.year)
            AnoAcademicoFin = etree.SubElement(Level3, "AnoAcademicoFin")
            AnoAcademicoFin.text = str(self.academic_year_id.date_end.year)
            if level_code == "3270":
                CodigoModalidad = etree.SubElement(Level3, "CodigoModalidad")
                CodigoModalidad.text = self.field_id.education_code

            # AreasConocimiento = etree.SubElement(Level3, "AreasConocimiento")
            # AreaConocimiento = etree.SubElement(AreasConocimiento, "AreaConocimiento")

            records = student.academic_record_ids.filtered(
                lambda r: r.n_line_id.schedule_id.academic_year_id.current)
            subjects = records.mapped("subject_id")

            MateriasBachillerato = etree.SubElement(Level3, "MateriasBachillerato")
            for subject in subjects:
                MateriaBachillerato = etree.SubElement(MateriasBachillerato, "MateriaBachillerato")
                CodigoAsignatura = etree.SubElement(MateriaBachillerato, "CodigoAsignatura")
                CodigoAsignatura.text = subject.education_code
                nota_ordinaria = records.filtered(
                    lambda r: r.subject_id == subject and
                    r.eval_type == "final" and not r.recovered_record_id)[:1]
                NotaNumericaOrdinaria = etree.SubElement(MateriaBachillerato, "NotaNumericaOrdinaria")
                numeric_mark = round(nota_ordinaria.numeric_mark + 0.00001, 0)
                NotaNumericaOrdinaria.text = "{:0>2d}".format(int(numeric_mark))

        return self.finalize_file_creation(xml_root, gen_args)

    @api.model
    def _validate_xml(self, xml_string, gen_args):
        xsd_etree_obj = etree.parse(
            tools.file_open(gen_args['xsd_file']))
        official_schema = etree.XMLSchema(xsd_etree_obj)

        try:
            root_to_validate = etree.fromstring(xml_string)
            official_schema.assertValid(root_to_validate)
        except Exception as e:
            logger.warning(
                "The XML file is invalid against the XML Schema Definition")
            logger.warning(xml_string)
            logger.warning(e)
            raise UserError(
                _("The generated XML file is not valid against the official "
                  "XML Schema Definition. The generated XML file and the "
                  "full error have been written in the server logs. Here "
                  "is the error, which may give you an idea on the cause "
                  "of the problem : %s")
                % str(e))
        return True

    @api.multi
    def finalize_file_creation(self, xml_root, gen_args):
        xml_string = etree.tostring(
            xml_root, pretty_print=True, encoding='UTF-8',
            xml_declaration=True)
        # logger.debug(
        #     "Generated SEPA XML file in format %s below"
        #     % gen_args['pain_flavor'])
        # logger.debug(xml_string)
        self._validate_xml(xml_string, gen_args)

        filename = '%s%s_%s.xml' % (gen_args['file_prefix'], self.center_id.name, self.education_code)
        return (xml_string, filename)

    @api.multi
    def export_xml(self):
        self.ensure_one()
        payment_file_str, filename = self.generate_xml_file()
        action = {}
        if payment_file_str and filename:
            attachment = self.env['ir.attachment'].create({
                'res_model': 'education.group',
                'res_id': self.id,
                'name': filename,
                'datas': base64.b64encode(payment_file_str),
                'datas_fname': filename,
                })
            simplified_form_view = self.env.ref(
                'account_payment_order.view_attachment_simplified_form')
            action = {
                'name': _('Payment File'),
                'view_mode': 'form',
                'view_id': simplified_form_view.id,
                'res_model': 'ir.attachment',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': attachment.id,
                }
        # self.write({
        #     'date_generated': fields.Date.context_today(self),
        #     'state': 'generated',
        #     'generated_user_id': self._uid,
        #     })
        return action
