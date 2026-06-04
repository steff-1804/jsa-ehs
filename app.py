from flask import Flask, render_template, request, send_file, jsonify
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as ExcelImage
from io import BytesIO
from PIL import Image
import json
import base64
import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 120 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/exportar_excel", methods=["POST"])
def exportar_excel():
    try:
        data = json.loads(request.form.get("data", "[]"))

        if not data:
            return jsonify({"error": "No hay datos para exportar"}), 400

        wb = Workbook()
        ws = wb.active
        ws.title = "Matriz JSA"

        thin = Side(border_style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        header_fill = PatternFill("solid", fgColor="1F4E79")
        subheader_fill = PatternFill("solid", fgColor="D9EAF7")
        hazard_fill = PatternFill("solid", fgColor="FCE4D6")
        control_fill = PatternFill("solid", fgColor="DAEEF3")
        recommended_fill = PatternFill("solid", fgColor="CCFF66")

        green_fill = PatternFill("solid", fgColor="86EFAC")
        yellow_fill = PatternFill("solid", fgColor="FDE047")
        red_fill = PatternFill("solid", fgColor="F87171")

        ws.merge_cells("A1:R1")
        ws["A1"] = "Risk Assessment / Job Hazard Analysis - Evaluación de Riesgos / Análisis de Peligros Laborales"
        ws["A1"].font = Font(bold=True, size=14, color="FFFFFF")
        ws["A1"].fill = header_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        ws.merge_cells("A2:C2")
        ws["A2"] = "Job / Activity Step"

        ws.merge_cells("D2:F2")
        ws["D2"] = "Hazard and Consequence"

        ws.merge_cells("G2:L2")
        ws["G2"] = "Existing / Current Condition Ranking"

        ws.merge_cells("M2:N2")
        ws["M2"] = "Recommended Controls"

        ws.merge_cells("O2:R2")
        ws["O2"] = "Post Rankings"

        section_cells = {
            "A2": subheader_fill,
            "D2": hazard_fill,
            "G2": control_fill,
            "M2": recommended_fill,
            "O2": subheader_fill
        }

        for cell_ref, fill in section_cells.items():
            ws[cell_ref].fill = fill
            ws[cell_ref].font = Font(bold=True)
            ws[cell_ref].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws[cell_ref].border = border

        headers = [
            "Área",
            "Actividad",
            "Foto",
            "Tipo riesgo",
            "Peligro",
            "Consecuencia",
            "SEV",
            "LIKL",
            "Existing Controls",
            "CONT",
            "RPN",
            "Recommended Controls",
            "SEV Post",
            "LIKL Post",
            "CONT Post",
            "RPN Post",
            "Observación",
            "Estado"
        ]

        header_row = 3

        for col_index, header in enumerate(headers, start=1):
            cell = ws.cell(row=header_row, column=col_index)
            cell.value = header
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.fill = subheader_fill
            cell.border = border

        data_start = 4

        for row_index, item in enumerate(data, start=data_start):
            sev = int(item.get("sev", 1))
            likl = int(item.get("likl", 1))
            cont = int(item.get("cont", 1))

            sev_post = int(item.get("sev_post", 1))
            likl_post = int(item.get("likl_post", 1))
            cont_post = int(item.get("cont_post", 1))

            rpn = sev * likl * cont
            rpn_post = sev_post * likl_post * cont_post

            values = [
                item.get("area", ""),
                item.get("actividad", ""),
                "",
                item.get("tipo_riesgo", ""),
                item.get("peligro", ""),
                item.get("consecuencia", ""),
                sev,
                likl,
                item.get("existing_controls", ""),
                cont,
                rpn,
                item.get("recommended_controls", ""),
                sev_post,
                likl_post,
                cont_post,
                rpn_post,
                "",
                ""
            ]

            for col_index, value in enumerate(values, start=1):
                cell = ws.cell(row=row_index, column=col_index)
                cell.value = value
                cell.border = border
                cell.alignment = Alignment(vertical="center", wrap_text=True)

            for col in [11, 16]:
                cell = ws.cell(row=row_index, column=col)

                if cell.value <= 10:
                    cell.fill = green_fill
                elif cell.value <= 30:
                    cell.fill = yellow_fill
                else:
                    cell.fill = red_fill

                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")

            foto_base64 = item.get("foto", "")

            if foto_base64:
                try:
                    if "," in foto_base64:
                        _, encoded = foto_base64.split(",", 1)
                    else:
                        encoded = foto_base64

                    image_data = base64.b64decode(encoded)
                    image_stream = BytesIO(image_data)

                    pil_image = Image.open(image_stream)
                    pil_image.thumbnail((180, 120))

                    final_stream = BytesIO()
                    pil_image.save(final_stream, format="PNG")
                    final_stream.seek(0)

                    excel_img = ExcelImage(final_stream)
                    excel_img.width = 150
                    excel_img.height = 100

                    ws.add_image(excel_img, f"C{row_index}")
                    ws.row_dimensions[row_index].height = 85

                except Exception:
                    ws.cell(row=row_index, column=3).value = "Imagen no válida"

        column_widths = {
            "A": 18,
            "B": 32,
            "C": 24,
            "D": 16,
            "E": 38,
            "F": 38,
            "G": 10,
            "H": 10,
            "I": 42,
            "J": 10,
            "K": 10,
            "L": 42,
            "M": 10,
            "N": 10,
            "O": 10,
            "P": 10,
            "Q": 20,
            "R": 18
        }

        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        ws.row_dimensions[1].height = 30
        ws.row_dimensions[2].height = 28
        ws.row_dimensions[3].height = 35

        ws.freeze_panes = "A4"

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            download_name="Matriz_JSA.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
