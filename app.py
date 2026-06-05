from flask import Flask, render_template, request, send_file, jsonify
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as ExcelImage
from io import BytesIO
from PIL import Image
import json
import base64

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 120 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/exportar_excel", methods=["POST"])
def exportar_excel():
    try:
        info_general = json.loads(request.form.get("info_general", "{}"))
        data = json.loads(request.form.get("data", "[]"))

        wb = Workbook()
        ws = wb.active
        ws.title = "Matriz JSA"

        thin = Side(border_style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        header_fill = PatternFill("solid", fgColor="1F4E79")
        subheader_fill = PatternFill("solid", fgColor="D9EAF7")
        green_fill = PatternFill("solid", fgColor="86EFAC")
        yellow_fill = PatternFill("solid", fgColor="FDE047")
        red_fill = PatternFill("solid", fgColor="F87171")

        ws.merge_cells("A1:N1")
        ws["A1"] = "MATRIZ JSA - ANÁLISIS SEGURO DE TRABAJO"
        ws["A1"].font = Font(bold=True, size=14, color="FFFFFF")
        ws["A1"].fill = header_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        ws["A2"] = "Área"
        ws["B2"] = info_general.get("area", "")
        ws["A3"] = "Miembros"
        ws["B3"] = info_general.get("miembros", "")
        ws["A4"] = "Fecha"
        ws["B4"] = info_general.get("fecha", "")
        ws["A5"] = "Descripción"
        ws["B5"] = info_general.get("descripcion", "")

        headers = [
            "Actividad", "Fotos", "Peligro", "Consecuencia",
            "SEV", "LIKL", "Controles existentes", "CONT", "RPN",
            "Controles recomendados", "SEV Post", "LIKL Post", "CONT Post", "RPN Post"
        ]

        start_row = 7

        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=start_row, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = subheader_fill
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        row = start_row + 1

        for item in data:
            sev = int(item.get("sev", 1))
            likl = int(item.get("likl", 1))
            cont = int(item.get("cont", 1))
            rpn = sev * likl * cont

            sev_post = int(item.get("sev_post", 1))
            likl_post = int(item.get("likl_post", 1))
            cont_post = int(item.get("cont_post", 1))
            rpn_post = sev_post * likl_post * cont_post

            values = [
                item.get("actividad", ""),
                "",
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
                rpn_post
            ]

            for col, value in enumerate(values, start=1):
                cell = ws.cell(row=row, column=col)
                cell.value = value
                cell.border = border
                cell.alignment = Alignment(vertical="center", wrap_text=True)

            for col in [9, 14]:
                cell = ws.cell(row=row, column=col)
                if cell.value <= 10:
                    cell.fill = green_fill
                elif cell.value <= 30:
                    cell.fill = yellow_fill
                else:
                    cell.fill = red_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")

            fotos = item.get("fotos", [])
            if fotos:
                for idx, foto_base64 in enumerate(fotos[:3]):
                    try:
                        encoded = foto_base64.split(",", 1)[1]
                        image_data = base64.b64decode(encoded)
                        image_stream = BytesIO(image_data)

                        pil_image = Image.open(image_stream)
                        pil_image.thumbnail((120, 90))

                        final_stream = BytesIO()
                        pil_image.save(final_stream, format="PNG")
                        final_stream.seek(0)

                        excel_img = ExcelImage(final_stream)
                        excel_img.width = 100
                        excel_img.height = 75

                        ws.add_image(excel_img, f"B{row + idx}")
                    except Exception:
                        ws.cell(row=row, column=2).value = "Imagen no válida"

                ws.row_dimensions[row].height = 70

            row += 1

        widths = {
            "A": 30, "B": 22, "C": 35, "D": 35,
            "E": 10, "F": 10, "G": 40, "H": 10, "I": 10,
            "J": 40, "K": 10, "L": 10, "M": 10, "N": 10
        }

        for col, width in widths.items():
            ws.column_dimensions[col].width = width

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Matriz_JSA.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
