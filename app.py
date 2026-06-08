from flask import Flask, render_template, request, send_file, jsonify
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as ExcelImage
from io import BytesIO
from PIL import Image
import json
import base64
import math

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


def pintar_rpn(cell):
    if cell.value <= 10:
        cell.fill = PatternFill("solid", fgColor="86EFAC")
    elif cell.value <= 30:
        cell.fill = PatternFill("solid", fgColor="FDE047")
    else:
        cell.fill = PatternFill("solid", fgColor="F87171")

    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center")


def insertar_foto_original(ws, fotos, celda, fila_inicio, fila_fin):
    if not fotos:
        return

    try:
        foto_base64 = fotos[0]

        if "," in foto_base64:
            encoded = foto_base64.split(",", 1)[1]
        else:
            encoded = foto_base64

        image_data = base64.b64decode(encoded)
        image_stream = BytesIO(image_data)

        pil_image = Image.open(image_stream)

        # NO se redimensiona la imagen.
        ancho_px, alto_px = pil_image.size

        final_stream = BytesIO()
        pil_image.save(final_stream, format="PNG")
        final_stream.seek(0)

        excel_img = ExcelImage(final_stream)

        # Se coloca en tamaño original.
        excel_img.width = ancho_px
        excel_img.height = alto_px

        ws.add_image(excel_img, celda)

        # Ajustar ancho de columna B según imagen.
        # Excel usa unidades aproximadas, 1 unidad ≈ 7 px.
        ancho_columna = max(32, min(ancho_px / 7, 120))
        ws.column_dimensions["B"].width = ancho_columna

        # Ajustar alto total de las filas combinadas.
        # Excel usa puntos, 1 px ≈ 0.75 pt.
        total_filas = max(1, fila_fin - fila_inicio + 1)
        alto_total_pt = alto_px * 0.75
        alto_por_fila = max(95, alto_total_pt / total_filas)

        for fila in range(fila_inicio, fila_fin + 1):
            ws.row_dimensions[fila].height = alto_por_fila

    except Exception:
        ws[celda] = "Imagen no válida"


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

        for row in range(2, 6):
            ws[f"A{row}"].font = Font(bold=True)
            ws[f"A{row}"].fill = subheader_fill
            ws[f"A{row}"].border = border
            ws[f"B{row}"].border = border
            ws[f"B{row}"].alignment = Alignment(wrap_text=True, vertical="center")

        headers = [
            "Actividad",
            "Fotos",
            "Peligro",
            "Consecuencia",
            "SEV",
            "LIKL",
            "Controles existentes",
            "CONT",
            "RPN",
            "Controles recomendados",
            "SEV Post",
            "LIKL Post",
            "CONT Post",
            "RPN Post"
        ]

        start_row = 7

        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=start_row, column=col)
            cell.value = header
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        row = start_row + 1
        actividad_inicio = {}

        for item in data:
            actividad_index = item.get("actividad_index", "")
            peligro_index = int(item.get("peligro_index", 0))
            total_peligros = int(item.get("total_peligros", 1))

            if peligro_index == 0:
                actividad_inicio[actividad_index] = row

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

            pintar_rpn(ws.cell(row=row, column=9))
            pintar_rpn(ws.cell(row=row, column=14))

            ws.row_dimensions[row].height = 95

            if peligro_index == total_peligros - 1:
                fila_inicio = actividad_inicio.get(actividad_index, row)
                fila_fin = row

                if fila_fin > fila_inicio:
                    ws.merge_cells(start_row=fila_inicio, start_column=1, end_row=fila_fin, end_column=1)
                    ws.merge_cells(start_row=fila_inicio, start_column=2, end_row=fila_fin, end_column=2)
                    ws.merge_cells(start_row=fila_inicio, start_column=7, end_row=fila_fin, end_column=7)
                    ws.merge_cells(start_row=fila_inicio, start_column=10, end_row=fila_fin, end_column=10)

                for col in [1, 2, 7, 10]:
                    ws.cell(row=fila_inicio, column=col).alignment = Alignment(
                        horizontal="center",
                        vertical="center",
                        wrap_text=True
                    )
                    ws.cell(row=fila_inicio, column=col).border = border

                fotos = item.get("fotos", [])

                # Si el último peligro no trae fotos, se buscan desde la primera fila de esa actividad
                if not fotos:
                    for buscar in data:
                        if (
                            buscar.get("actividad_index") == actividad_index
                            and int(buscar.get("peligro_index", 0)) == 0
                        ):
                            fotos = buscar.get("fotos", [])
                            break

                insertar_foto_original(
                    ws,
                    fotos,
                    f"B{fila_inicio}",
                    fila_inicio,
                    fila_fin
                )

            row += 1

        widths = {
            "A": 30,
            "B": 45,
            "C": 34,
            "D": 38,
            "E": 10,
            "F": 10,
            "G": 42,
            "H": 10,
            "I": 10,
            "J": 42,
            "K": 10,
            "L": 10,
            "M": 10,
            "N": 10
        }

        for col, width in widths.items():
            if col != "B":
                ws.column_dimensions[col].width = width

        ws.row_dimensions[1].height = 30
        ws.row_dimensions[7].height = 38
        ws.freeze_panes = "A8"

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
