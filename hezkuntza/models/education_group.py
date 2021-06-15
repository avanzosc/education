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
            "file_prefix": "hezkuntza_",
            "xsd_file": xsd_file,
        }
        xml_root = etree.Element("DatosHistoriales")
        codigo_centro = etree.SubElement(
            xml_root, "CodigoCentroJuridico")
        codigo_centro.text = self.center_id.education_code

        level_code = self.level_id.hezkuntza_level
        if level_code == "1120":
            level1 = "Primaria"
            cursos_tag = "CursosPrimaria"
            curso_tag = "CursoPrimaria"
            materias_tag = "AreasConocimiento"
            materia_tag = "AreaConocimiento"
            grade_tag = "NotaNumerica"
        elif level_code == "2260":
            level1 = "Secundaria"
            cursos_tag = "CursosSecundaria"
            curso_tag = "CursoSecundaria"
            materias_tag = "MateriasSecundaria"
            materia_tag = "MateriaSecundaria"
            grade_tag = "NotaNumericaOrdinaria"
        elif level_code == "3270":
            level1 = "Bachillerato"
            cursos_tag = "CursosBachillerato"
            curso_tag = "CursoBachillerato"
            materias_tag = "MateriasBachillerato"
            materia_tag = "MateriaBachillerato"
            grade_tag = "NotaNumericaOrdinaria"
        else:
            level1 = "FP"
            cursos_tag = "CiclosFormativos"
            curso_tag = "CicloFormativo"
            grade_tag = "NotaNumericaOrdinaria"

        for student in self.student_ids:
            history = etree.SubElement(xml_root, "Historial")
            common_data = etree.SubElement(
                history, "DatosComunes")
            NivelEducativo = etree.SubElement(
                common_data, "NivelEducativo")
            CodigoNivelEducativo = etree.SubElement(
                NivelEducativo, "CodigoNivelEducativo")
            CodigoNivelEducativo.text = level_code

            IdentificacionAlumno = etree.SubElement(
                common_data, "IdentificacionAlumno")
            center_code = etree.SubElement(
                IdentificacionAlumno, "CodigoCentro")
            student_code = etree.SubElement(center_code, "CodigoAlumno")
            education_code = student.education_code
            if not education_code.isdigit():
                education_code = education_code[:-1]

            student_code.text = education_code.zfill(10)

            Level1 = etree.SubElement(history, level1)
            cursos = etree.SubElement(Level1, cursos_tag)
            curso = etree.SubElement(cursos, curso_tag)

            centro_element = etree.SubElement(curso, "Centro")
            center_code_element = etree.SubElement(
                centro_element, "CodigoCentroJuridico")
            center_code_element.text = self.center_id.education_code
            course_value = etree.SubElement(curso, "ValorCurso")
            course_value.text = str(self.course_id.course_value or 0)
            start_year = self.academic_year_id.date_start.year
            end_year = self.academic_year_id.date_end.year
            academic_year_start = etree.SubElement(curso, "AnoAcademicoInicio")
            academic_year_start.text = str(start_year)
            academic_year_end = etree.SubElement(curso, "AnoAcademicoFin")
            academic_year_end.text = str(end_year)
            if level_code == "3270":
                field_element = etree.SubElement(curso, "CodigoModalidad")
                field_element.text = self.field_id.education_code
                regimen = etree.SubElement(curso, "CodigoRegimen")
                regimen.text = "1"
            records = student.academic_record_ids.filtered(
                lambda r: r.n_line_id.schedule_id.academic_year_id.current)
            if records and level_code in ["1120", "2260", "3270"]:
                subjects = records.mapped("subject_id")
                Materias = etree.SubElement(curso, materias_tag)
                for subject in subjects:
                    Materia = etree.SubElement(Materias, materia_tag)
                    CodigoAsignatura = etree.SubElement(
                        Materia, "CodigoAsignatura")
                    CodigoAsignatura.text = subject.education_code
                    nota_ordinaria = records.filtered(
                        lambda r: r.subject_id == subject and
                        r.eval_type == "final" and
                        not r.recovered_record_id)[:1]
                    grade = etree.SubElement(Materia, grade_tag)
                    if nota_ordinaria.exceptionality == "exempt":
                        grade.text = "13"
                    elif nota_ordinaria.exceptionality == "not_evaluated":
                        grade.text = "14"
                    elif nota_ordinaria.exceptionality == "not_taken":
                        grade.text = "15"
                    else:
                        num_mark = round(
                            nota_ordinaria.numeric_mark + 0.00001, 0)
                        grade.text = "{:0>2d}".format(int(num_mark))
                    if level_code != "1120":
                        aci_element = etree.SubElement(Materia, "ACI")
                        if nota_ordinaria.exceptionality == "adaptation":
                            aci_element.text = "S"
                        else:
                            aci_element.text = "N"

        return self.finalize_file_creation(xml_root, gen_args)

    @api.model
    def _validate_xml(self, xml_string, gen_args):
        xsd_etree_obj = etree.parse(
            tools.file_open(gen_args["xsd_file"]))
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
            xml_root, pretty_print=True, encoding="UTF-8",
            xml_declaration=True)
        self._validate_xml(xml_string, gen_args)

        filename = "{}{}_{}.xml".format(
            gen_args["file_prefix"], self.center_id.name, self.education_code)
        return (xml_string, filename)

    @api.multi
    def export_xml(self):
        self.ensure_one()
        payment_file_str, filename = self.generate_xml_file()
        action = {}
        if payment_file_str and filename:
            attachment = self.env["ir.attachment"].create({
                "res_model": "education.group",
                "res_id": self.id,
                "name": filename,
                "datas": base64.b64encode(payment_file_str),
                "datas_fname": filename,
            })
            simplified_form_view = self.env.ref(
                "hezkuntza.view_attachment_simplified_form")
            action = {
                "name": _("Export Education Records XML"),
                "view_mode": "form",
                "view_id": simplified_form_view.id,
                "res_model": "ir.attachment",
                "type": "ir.actions.act_window",
                "target": "current",
                "res_id": attachment.id,
            }
        return action
