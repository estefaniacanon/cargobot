# Plan de Desarrollo: Sistema de Seguimiento de Camiones

## Visión General

Sistema automatizado para control de tráfico y seguimiento de camiones, compuesto por:
1. **Procesador de CSV** - Lee archivos de Amazon Relay
2. **Dashboard HTML** - Interfaz interactiva con semáforo y gestión

---

## Fase 1: Procesador de CSV

### 1.1 Lector de Carpeta
- Escanea directorio configurable
- Detecta archivos CSV nuevos de Amazon Relay
- Soporte para múltiples archivos simultáneos

### 1.2 Parser de Amazon Relay
Campos a extraer:
| Campo | Descripción |
|-------|-------------|
| ID de viaje | Identificador del tour completo (T-xxxxxx) |
| ID de VR | Identificador de cada sección/tramo |
| Estado | COMPLETED, IN_TRANSIT, PLANNED |
| Conductor | Nombre del chófer |
| 1 Parada / 2 Parada / 3 Parada | Ubicaciones de carga/descarga |
| Llegada al patio N | Fechas y horas de llegada |
| Cuenta del remitente | Tipo de operación (ATSOutbound, FleetManagementEquipmentRepositioning, etc.) |
| ID del bloque | Identificador de tour (para distinguir viajes sueltos de tours) |

### 1.3 Normalizador
- Genera JSON con todos los registros
- NO aplica filtros de jornada (se hace en dashboard)
- Conserva estructura original para permitir filtros dinámicos

---

## Fase 2: Dashboard HTML

### 2.1 Configuración de Jornada
- **Rango horario**: 06:00 - 15:00 (configurable)
- **Fecha de trabajo**: selectable
- Filtro dinámico: muestra solo viajes con acción dentro del rango

### 2.2 Semáforo de Alertas
| Color | Condición |
|-------|-----------|
| 🟢 Verde | >2 horas para la acción |
| 🟡 Amarillo | <2 horas (llamar pronto) |
| 🔴 Rojo | <5 minutos (llamar ahora) |
| ⏳ Gris | Sin acción en jornada |

### 2.3 Sistema de Gestión
Estados por viaje:
- **Pendiente llamar** - Sin gestionar
- **Contactado OK** - Llamada realizada, todo bien
- **Retraso** - El chófer informa de retraso
- **Sin respuesta** - No se ha podido contactar
- **Incidencia** - Problema reportado
- **Cargado ✓** - Confirmación de carga
- **Descargado ✓** - Confirmación de descarga (cierra el viaje)

### 2.4 Gestión de Tours
- Muestra ID de tour (T-xxxxxx) + ID de VR de cada sección
- Filtro para excluir tours vacíos (FleetManagementEquipmentRepositioning en tours)
- Incluye viajes vacíos sueltos

### 2.5 Viajes "EN VUELO"
- IN_TRANSIT de días anteriores sin confirmar llegada
- Marcados en amarillo para seguimiento especial
- Incluidos siempre al inicio de cada jornada

### 2.6 Persistencia
- localStorage para gestionar estado entre sesiones
- Botón "Nueva jornada" para limpiar datos
- Indicador visual de guardado

### 2.7 KPIs en Tiempo Real
- Total de viajes del día
- 🟢 En tiempo
- ⏳ Pendientes sin confirmar
- ✓ Confirmados (cargado/descargado)

---

## Fase 3: Mejoras Futuras (opcional)

- Publicación web (GitHub Pages / Netlify)
- Sincronización multi-usuario
- Historial de jornadas
- Integración con APIs de notificaciones

---

## Criterios de Filtrado Definitivos

### Incluir viaje si:
1. Al menos UNA parada (carga O descarga) cae entre 06:00-15:00
2. Es IN_TRANSIT de día anterior sin confirmar (EN VUELO)

### Excluir:
1. Estado COMPLETED
2. Viajes con FleetManagementEquipmentRepositioning que SON de tour
3. Viajes sin ninguna acción en la jornada

### Incluir siempre:
1. Viajes vacíos SUELTOS (no de tour)
2. Tours con FleetManagementEquipmentRepositioning (porque son parte del tour)
3. RailTrailerPoolAdjustment (tratar como cualquier otro viaje)

---

## Formato de Datos

### JSON de entrada (desde CSV)
```json
{
  "fecha": "2026-03-12",
  "secciones": [
    {
      "id_viaje": "T-114ZW7GJ1",
      "id_vr": "113GBQJCY",
      "estado": "IN_TRANSIT",
      "conductor": "Nombre del conductor",
      "cuenta": "ATSOutbound",
      "es_tour": true,
      "paradas": [
        {"tipo": "carga", "ubicacion": "DQL2", "llegada": "2026-03-12T05:30:00"},
        {"tipo": "descarga", "ubicacion": "MAD9", "llegada": "2026-03-12T09:48:00"}
      ]
    }
  ]
}
```

### Objeto de gestión (localStorage)
```json
{
  "fecha": "2026-03-12",
  "gestiones": {
    "113GBQJCY": {
      "estado": "incidencia",
      "notas": "Retraso por tráfico",
      "timestamp": "2026-03-12T08:15:00"
    }
  }
}
```
