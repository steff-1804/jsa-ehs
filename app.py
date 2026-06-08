from flask import Flask, render_template, request, send_file, jsonify
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as ExcelImage
from io import BytesIO
from PIL import Image
import json
import base64

app = Flask(__name__)

# Permite archivos/fotos grandes. En Render evita pasarte demasiado de peso.
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


def limpiar_base64(foto_base64):
    if "," in foto_base64:
        return foto_base64.split(",", 1)[1]
    return foto_base64


def insertar_foto_en_excel(ws, fotos, celda, fila_inicio, fila_fin):
    """
    Inserta la primera foto de la actividad sin deformarla.
    La imagen se ajusta proporcionalmente si es demasiado grande para Excel.
    La celda combinada se expande en alto para que se vea mejor.
    """
    if not fotos:
        return

    try:
        foto_base64 = fotos[0]
        encoded = limpiar_base64(foto_base64)

        image_data = base64.b64decode(encoded)
        image_stream = BytesIO(image_data)

        pil_image = Image.open(image_stream)
        pil_image = pil_image.convert("RGB")

        ancho_original, alto_original = pil_image.size

        # Máximos razonables para que Excel no se rompa ni Render falle.
        # Mantiene proporción, NO deforma la imagen.
        max_ancho = 520
        max_alto = 380

        escala = min(
            max_ancho / ancho_original,
            max_alto / alto_original,
            1
        )

        nuevo_ancho = int(ancho_original * escala)
        nuevo_alto = int(alto_original * escala)

        if escala < 1:
            pil_image = pil_image.resize(
                (nuevo_ancho, nuevo_alto),
                Image.LANCZOS
            )

        final_stream = BytesIO()
        pil_image.save(final_stream, format="PNG", optimize=True)
        final_stream.seek(0)

        excel_img = ExcelImage(final_stream)
        excel_img.width = nuevo_ancho
        excel_img.height = nuevo_alto

        ws.add_image(excel_img, celda)

        # Ajustar columna B según la imagen.
        # Excel usa unidades aproximadas: 1 unidad ≈ 7 px.
        ws.column_dimensions["B"].width = max(35, min(nuevo_ancho / 7, 80))

        # Ajustar alto de las filas combinadas según imagen.
        total_filas = max(1, fila_fin - fila_inicio + 1)
        alto_total_pt = nuevo_alto * 0.75
        alto_por_fila = max(95, alto_total_pt / total_filas)

        for fila in range(fila_inicio, fila_fin + 1):
            ws.row_dimensions[fila].height = alto_por_fila

    except Exception as e:
        ws[celda] = f"Imagen no válida: {str(e)}"


@app.route("/exportar_excel", methods=["POST"])
def exportar_excel():
    try:
        info_general = json.loads(request.form.get("info_general", "{}"))
        data = json.loads(request.form.get("data", "[]"))

        if not data:
            return jsonify({"error": "No hay datos para exportar."}), 400

        wb = Workbook()
        ws = wb.active
        ws.title = "Matriz JSA"

        thin = Side(border_style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        header_fill = PatternFill("solid", fgColor="1F4E79")
        subheader_fill = PatternFill("solid", fgColor="D9EAF7")
        info_fill = PatternFill("solid", fgColor="F8FBFF")

        # Título
        ws.merge_cells("A1:N1")
        ws["A1"] = "MATRIZ JSA - ANÁLISIS SEGURO DE TRABAJO"
        ws["A1"].font = Font(bold=True, size=14, color="FFFFFF")
        ws["A1"].fill = header_fill
        ws["A1"].alignment = Alignment(
            horizontal="center",
            vertical="center"
        )
        ws["A1"].border = border
        ws.row_dimensions[1].height = 30

        # Información general
        info_rows = [
            ("Área", info_general.get("area", "")),
            ("Miembros", info_general.get("miembros", "")),
            ("Fecha", info_general.get("fecha", "")),
            ("Descripción", info_general.get("descripcion", ""))
        ]

        start_info_row = 2

        for i, (label, value) in enumerate(info_rows, start=start_info_row):
            ws.cell(row=i, column=1).value = label
            ws.cell(row=i, column=1).font = Font(bold=True)
            ws.cell(row=i, column=1).fill = subheader_fill
            ws.cell(row=i, column=1).border = border
            ws.cell(row=i, column=1).alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True
            )

            ws.merge_cells(
                start_row=i,
                start_column=2,
                end_row=i,
                end_column=14
            )

            ws.cell(row=i, column=2).value = value
            ws.cell(row=i, column=2).fill = info_fill
            ws.cell(row=i, column=2).border = border
            ws.cell(row=i, column=2).alignment = Alignment(
                vertical="center",
                wrap_text=True
            )

            ws.row_dimensions[i].height = 28

        # Encabezados
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
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True
            )

        ws.row_dimensions[start_row].height = 42

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
                cell.alignment = Alignment(
                    vertical="center",
                    horizontal="center" if col in [5, 6, 8, 9, 11, 12, 13, 14] else "left",
                    wrap_text=True
                )

            pintar_rpn(ws.cell(row=row, column=9))
            pintar_rpn(ws.cell(row=row, column=14))

            ws.row_dimensions[row].height = 95

            # Al llegar al último peligro de la actividad, combinar celdas.
            if peligro_index == total_peligros - 1:
                fila_inicio = actividad_inicio.get(actividad_index, row)
                fila_fin = row

                columnas_a_combinar = [1, 2, 7, 10]

                if fila_fin > fila_inicio:
                    for col in columnas_a_combinar:
                        ws.merge_cells(
                            start_row=fila_inicio,
                            start_column=col,
                            end_row=fila_fin,
                            end_column=col
                        )

                # Alineación y borde de las celdas combinadas.
                for col in columnas_a_combinar:
                    cell = ws.cell(row=fila_inicio, column=col)
                    cell.alignment = Alignment(
                        horizontal="center",
                        vertical="center",
                        wrap_text=True
                    )
                    cell.border = border

                # Buscar fotos de la primera fila de la actividad.
                fotos = item.get("fotos", [])

                if not fotos:
                    for buscar in data:
                        if (
                            buscar.get("actividad_index") == actividad_index
                            and int(buscar.get("peligro_index", 0)) == 0
                        ):
                            fotos = buscar.get("fotos", [])
                            break

                insertar_foto_en_excel(
                    ws=ws,
                    fotos=fotos,
                    celda=f"B{fila_inicio}",
                    fila_inicio=fila_inicio,
                    fila_fin=fila_fin
                )

            row += 1

        # Anchos de columnas
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

        # Congelar encabezado
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
