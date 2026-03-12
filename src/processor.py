"""
Procesador de CSV para Amazon Relay.
Lee archivos CSV de una carpeta y genera un JSON normalizado.
"""
import os
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "src" / "output"
OUTPUT_FILE = OUTPUT_DIR / "data.json"


def parse_date(date_str):
    """
    Convierte fecha de formato DD/MM/YYYY HH:mm a ISO 8601.
    
    Args:
        date_str: Cadena con formato DD/MM/YYYY HH:mm
        
    Returns:
        Cadena en formato ISO 8601 o None si es inválida
    """
    if not date_str or date_str.lower() == "nan":
        return None
    
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y %H:%M")
        return dt.isoformat()
    except ValueError:
        return None


def clean_value(value):
    """
    Limpia valores del CSV eliminando comillas y espacios.
    
    Args:
        value: Valor original del CSV
        
    Returns:
        Valor limpio o cadena vacía
    """
    if value is None:
        return ""
    return value.strip().replace('"', '').replace("'", "")


def parse_row(row, headers):
    """
    Procesa una fila del CSV y la convierte a diccionario.
    
    Args:
        row: Lista de valores de la fila
        headers: Lista de nombres de columnas
        
    Returns:
        Diccionario con los datos normalizados
    """
    def get_val(name):
        if name not in headers:
            return ""
        idx = headers.index(name)
        if idx >= len(row):
            return ""
        return clean_value(row[idx])
    
    id_viaje = get_val("ID de viaje")
    id_bloque = get_val("ID del bloque")
    es_tour = bool(id_bloque and id_bloque.lower() != "nan")
    
    cancelacion = get_val("Fecha y hora de cancelacion")
    cancelado = bool(cancelacion and cancelacion.lower() != "nan")
    
    paradas = []
    
    p1 = get_val("1 Parada")
    l1 = get_val("Llegada al patio 1 de parada")
    if p1 and p1.lower() != "nan":
        paradas.append({
            "tipo": "carga",
            "ubicacion": p1,
            "llegada": parse_date(l1)
        })
    
    p2 = get_val("2 Parada")
    l2 = get_val("Llegada al patio 2 de parada")
    if p2 and p2.lower() != "nan":
        paradas.append({
            "tipo": "descarga",
            "ubicacion": p2,
            "llegada": parse_date(l2)
        })
    
    p3 = get_val("3 Parada")
    l3 = get_val("Llegada al patio 3 de parada")
    if p3 and p3.lower() != "nan":
        paradas.append({
            "tipo": "descarga",
            "ubicacion": p3,
            "llegada": parse_date(l3)
        })
    
    return {
        "id_viaje": id_viaje,
        "id_vr": get_val("ID de VR"),
        "estado": get_val("Estado"),
        "conductor": get_val("Conductor"),
        "cuenta": get_val("Cuenta del remitente"),
        "id_bloque": id_bloque if es_tour else None,
        "es_tour": es_tour,
        "cancelado": cancelado,
        "paradas": paradas
    }


def read_csv_file(filepath):
    """
    Lee un archivo CSV y devuelve una lista de diccionarios.
    
    Args:
        filepath: Ruta al archivo CSV
        
    Returns:
        Lista de diccionarios con los datos
    """
    secciones = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        headers = [h.strip().replace('"', '') for h in headers]
        
        for row in reader:
            if not row or not row[0].strip():
                continue
            
            seccion = parse_row(row, headers)
            
            if seccion["id_viaje"] and seccion["id_viaje"].lower() != "nan":
                secciones.append(seccion)
    
    return secciones


def get_csv_files():
    """
    Obtiene lista de archivos CSV en la carpeta data.
    
    Returns:
        Lista de rutas a archivos CSV
    """
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return []
    
    csv_files = [f for f in DATA_DIR.iterdir() if f.suffix.lower() == ".csv"]
    return sorted(csv_files)


def process_csv_files():
    """
    Procesa todos los archivos CSV de la carpeta data.
    
    Returns:
        Diccionario con los datos procesados
    """
    csv_files = get_csv_files()
    
    if not csv_files:
        print("No se encontraron archivos CSV en la carpeta data/")
        return None
    
    print(f"Se encontraron {len(csv_files)} archivo(s) CSV")
    
    all_sections = []
    processed_files = []
    
    for csv_file in csv_files:
        print(f"Procesando: {csv_file.name}")
        sections = read_csv_file(csv_file)
        all_sections.extend(sections)
        processed_files.append(csv_file.name)
    
    output_data = {
        "fecha_procesamiento": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "archivos_procesados": processed_files,
        "total_secciones": len(all_sections),
        "secciones": all_sections
    }
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Se procesaron {len(all_sections)} secciones")
    print(f"JSON guardado en: {OUTPUT_FILE}")
    
    return output_data


def main():
    """Función principal."""
    process_csv_files()


if __name__ == "__main__":
    main()
