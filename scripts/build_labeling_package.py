"""Script generador de paquete de etiquetado ciego de temas (CRISP-DM Bloque 0)."""
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PATH = ROOT / "data" / "processed" / "model_outputs" / "theme_review_sample.csv"
OUT_DIR = ROOT / "data" / "processed" / "model_outputs"

if not SAMPLE_PATH.exists():
    raise FileNotFoundError(f"No se encontró el archivo de muestra en {SAMPLE_PATH}")

df = pd.read_csv(SAMPLE_PATH, encoding="utf-8-sig")

# 1. theme_labeling_clave.csv
clave_df = pd.DataFrame({
    "id_fila": range(1, len(df) + 1),
    "comment_id": df["comment_id"],
    "plataforma": df["platform"]
})
clave_df.to_csv(OUT_DIR / "theme_labeling_clave.csv", index=False, encoding="utf-8-sig")

# 2. Plantilla para Anotador A y B (CSV ciego)
labeling_df = pd.DataFrame({
    "id_fila": range(1, len(df) + 1),
    "plataforma": df["platform"],
    "texto": df["text"],
    "tema": ["" for _ in range(len(df))],
    "ambiguo": ["" for _ in range(len(df))],
    "necesita_contexto": ["" for _ in range(len(df))],
    "notas": ["" for _ in range(len(df))]
})

labeling_df.to_csv(OUT_DIR / "theme_labeling_anotador_A.csv", index=False, encoding="utf-8-sig")
labeling_df.to_csv(OUT_DIR / "theme_labeling_anotador_B.csv", index=False, encoding="utf-8-sig")

options = [
    "Protesta y movilización",
    "Programas de acceso y bienestar",
    "Admisiones, inscripciones y matrículas",
    "Información, trámites y certificados",
    "Oferta académica e investigación",
    "Infraestructura, sedes y tecnología",
    "Eventos, cultura y actividades institucionales",
    "Felicitaciones y expresiones de aprecio",
    "Otro tema identificable",
    "Sin contenido temático",
    "Ambiguo"
]

def create_excel(filepath: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Etiquetado"

    ws_options = wb.create_sheet(title="Opciones_Validacion")
    for idx, opt in enumerate(options, 1):
        ws_options.cell(row=idx, column=1, value=opt)
    ws_options.sheet_state = "hidden"

    headers = ["id_fila", "plataforma", "texto", "tema", "ambiguo", "necesita_contexto", "notas"]
    ws.append(headers)

    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for _, row in labeling_df.iterrows():
        ws.append([
            row["id_fila"],
            row["plataforma"],
            row["texto"],
            "",
            "",
            "",
            ""
        ])

    align_top_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
    align_center = Alignment(horizontal="center", vertical="top")

    for r in range(2, len(labeling_df) + 2):
        ws.cell(row=r, column=1).alignment = align_center
        ws.cell(row=r, column=2).alignment = align_center
        ws.cell(row=r, column=3).alignment = align_top_left
        ws.cell(row=r, column=4).alignment = align_top_left
        ws.cell(row=r, column=5).alignment = align_center
        ws.cell(row=r, column=6).alignment = align_center
        ws.cell(row=r, column=7).alignment = align_top_left

    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 65
    ws.column_dimensions["D"].width = 44
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 35

    formula_opts = "Opciones_Validacion!$A$1:$A$11"
    dv_tema = DataValidation(type="list", formula1=formula_opts, allow_blank=True)
    dv_tema.error = "Por favor seleccione una categoría válida de la lista"
    dv_tema.errorTitle = "Categoría inválida"
    dv_tema.prompt = "Seleccione una categoría de la lista"
    dv_tema.promptTitle = "Tema"
    ws.add_data_validation(dv_tema)
    dv_tema.add(f"D2:D{len(labeling_df) + 1}")

    formula_sino = '"si,no"'
    dv_sino = DataValidation(type="list", formula1=formula_sino, allow_blank=True)
    ws.add_data_validation(dv_sino)
    dv_sino.add(f"E2:E{len(labeling_df) + 1}")
    dv_sino.add(f"F2:F{len(labeling_df) + 1}")

    wb.save(filepath)

create_excel(OUT_DIR / "theme_labeling_anotador_A.xlsx")
create_excel(OUT_DIR / "theme_labeling_anotador_B.xlsx")
print("Archivos de etiquetado A, B y clave generados exitosamente.")
