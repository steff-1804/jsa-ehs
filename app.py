from flask import Flask, render_template, request, send_file
from openpyxl import Workbook
from io import BytesIO
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/exportar_excel", methods=["POST"])
def exportar_excel():

    info_general = json.loads(
        request.form.get("info_general", "{}")
    )

    actividades = json.loads(
        request.form.get("data", "[]")
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Matriz JSA"

    ws["A1"] = "AREA"
    ws["B1"] = info_general.get("area", "")

    ws["A2"] = "MIEMBROS"
    ws["B2"] = info_general.get("miembros", "")

    ws["A3"] = "FECHA"
    ws["B3"] = info_general.get("fecha", "")

    ws["A4"] = "DESCRIPCION"
    ws["B4"] = info_general.get("descripcion", "")

    encabezados = [
        "Actividad",
        "Peligro",
        "Consecuencia",
        "SEV",
        "LIKL",
        "Controles Existentes",
        "CONT",
        "RPN",
        "Controles Recomendados",
        "SEV POST",
        "LIKL POST",
        "CONT POST",
        "RPN POST"
    ]

    fila_inicio = 7

    for col, encabezado in enumerate(encabezados, start=1):
        ws.cell(
            row=fila_inicio,
            column=col,
            value=encabezado
        )

    fila = fila_inicio + 1

    for item in actividades:

        sev = int(item.get("sev", 1))
        likl = int(item.get("likl", 1))
        cont = int(item.get("cont", 1))

        rpn = sev * likl * cont

        sev_post = int(item.get("sev_post", 1))
        likl_post = int(item.get("likl_post", 1))
        cont_post = int(item.get("cont_post", 1))

        rpn_post = sev_post * likl_post * cont_post

        ws.cell(fila, 1, item.get("actividad", ""))
        ws.cell(fila, 2, item.get("peligro", ""))
        ws.cell(fila, 3, item.get("consecuencia", ""))

        ws.cell(fila, 4, sev)
        ws.cell(fila, 5, likl)

        ws.cell(
            fila,
            6,
            item.get("existing_controls", "")
        )

        ws.cell(fila, 7, cont)
        ws.cell(fila, 8, rpn)

        ws.cell(
            fila,
            9,
            item.get("recommended_controls", "")
        )

        ws.cell(fila, 10, sev_post)
        ws.cell(fila, 11, likl_post)
        ws.cell(fila, 12, cont_post)
        ws.cell(fila, 13, rpn_post)

        fila += 1

    output = BytesIO()

    wb.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Matriz_JSA.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    app.run(debug=True)
