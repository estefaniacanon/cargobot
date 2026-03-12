# Fase 1: Procesador de CSV

## Objetivo

Leer archivos CSV de Amazon Relay desde una carpeta, procesarlos y generar un archivo JSON estandarizado con todos los registros, sin aplicar filtros de jornada.

---

## 1. Estructura de Carpetas

```
cargobot/
├── data/                    # Archivos CSV de entrada
│   ├── 10032026_ACELC.csv
│   └── 10032026_AVNHE.csv
├── src/                     # Código fuente
├── output/                  # JSON generado
│   └── data.json
└── docs/                    # Documentación
```

---

## 2. Lector de Carpeta

### Requisitos
- Escanea el directorio `data/` automáticamente
- Detecta archivos con extensión `.csv`
- Soporte para múltiples archivos simultáneos
- Ignora archivos que no sean CSV

### Comportamiento
1. Lista todos los archivos `.csv` en la carpeta
2. Procesa cada archivo secuencialmente
3. Combina los resultados en un solo JSON

---

## 3. Parser de Amazon Relay

### Campos a Extraer

| Campo CSV | Campo JSON | Descripción |
|-----------|------------|-------------|
| ID de viaje | `id_viaje` | Identificador del tour (T-xxxxxx) |
| ID de VR | `id_vr` | Identificador único de cada sección |
| Estado | `estado` | COMPLETED, IN_TRANSIT, PLANNED |
| Conductor | `conductor` | Nombre del chófer |
| 1 Parada | `paradas[0].ubicacion` | Código de ubicación |
| Llegada al patio 1 de parada | `paradas[0].llegada` | Fecha y hora (ISO 8601) |
| 2 Parada | `paradas[1].ubicacion` | Código de ubicación |
| Llegada al patio 2 de parada | `paradas[1].llegada` | Fecha y hora |
| 3 Parada | `paradas[2].ubicacion` | Código de ubicación |
| Llegada al patio 3 de parada | `paradas[2].llegada` | Fecha y hora |
| Cuenta del remitente | `cuenta` | Tipo de operación |
| ID del bloque | `id_bloque` | Identificador de tour |
| Fecha y hora de cancelacion | `cancelado` | Boolean |

---

## 4. Lógica de Parsing

### 4.1 Detección de Tours
- Si `ID del bloque` existe y no es vacío → `es_tour: true`
- Si `ID del bloque` está vacío → `es_tour: false`

### 4.2 Procesamiento de Paradas
Cada parada se estructura como:
```json
{
  "tipo": "carga" | "descarga",
  "ubicacion": "DQL2",
  "llegada": "2026-03-12T05:30:00"
}
```

- **1ª Parada** → siempre tipo `carga`
- **2ª y 3ª Parada** → siempre tipo `descarga`

### 4.3 Conversión de Fechas
- Formato entrada: `DD/MM/YYYY HH:mm`
- Formato salida: `YYYY-MM-DDTHH:mm:ss` (ISO 8601)
- Si campo vacío o `nan` → omitir parada

### 4.4 Cancelaciones
- Si `Fecha y hora de cancelacion` tiene valor → `cancelado: true`
- Si campo vacío o `nan` → `cancelado: false`

---

## 5. Normalizador

### 5.1 Salida JSON
El procesador genera un JSON con estructura:

```json
{
  "fecha_procesamiento": "2026-03-12T08:00:00Z",
  "archivos_procesados": ["10032026_ACELC.csv", "10032026_AVNHE.csv"],
  "total_secciones": 45,
  "secciones": [
    {
      "id_viaje": "T-114ZW7GJ1",
      "id_vr": "113GBQJCY",
      "estado": "IN_TRANSIT",
      "conductor": "Juan García",
      "cuenta": "ATSOutbound",
      "id_bloque": "B-5ZLHVDKXT",
      "es_tour": true,
      "cancelado": false,
      "paradas": [
        {
          "tipo": "carga",
          "ubicacion": "DQL2",
          "llegada": "2026-03-12T05:30:00"
        },
        {
          "tipo": "descarga",
          "ubicacion": "MAD9",
          "llegada": "2026-03-12T09:48:00"
        }
      ]
    }
  ]
}
```

### 5.2 Reglas
- **NO aplica filtros de jornada** - guarda todos los registros
- **NO excluye COMPLETED** - se conserva el estado original
- **Combina múltiples CSVs** - concatena secciones

---

## 6. Casos Edge

| Caso | Comportamiento |
|------|----------------|
| CSV vacío | Genera JSON con array vacío |
| Campo con valor "nan" | Tratar como vacío |
| Filas sin ID de viaje | Omitir |
| Comillas en valores | Limpiar comillas |
| Múltiples commas en celda | Manejar CSV correctamente |

---

## 7. Métricas de Salida

El JSON incluye metadatos:
- `fecha_procesamiento`: Timestamp del procesamiento
- `archivos_procesados`: Lista de archivos leídos
- `total_secciones`: Conteo total de registros

---

## 8. Próximo Paso

El JSON generado será consumido por el **Dashboard (Fase 2)**, que aplicará los filtros de jornada y mostrará la interfaz interactiva.
