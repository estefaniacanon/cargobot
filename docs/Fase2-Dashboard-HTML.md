# Fase 2: Dashboard HTML

## Objetivo

Interfaz web interactiva que lee el JSON generado por la Fase 1, aplica los filtros de jornada y permite gestionar el seguimiento de camiones en tiempo real.

---

## 1. Configuración de Jornada

### Parámetros
- **Rango horario**: 06:00 - 15:00 (configurable por el usuario)
- **Fecha de trabajo**: selectable (por defecto, hoy)

### Comportamiento
- El usuario puede ajustar el rango de jornada desde la interfaz
- Los filtros se aplican en tiempo real sin recargar

---

## 2. Filtros de Jornada

### 2.1 Viajes Incluidos
Un viaje se muestra si cumple AL MENOS UNA de estas condiciones:
1. **Tiene acción en jornada**: Al menos una parada (carga O descarga) cae entre el rango horario configurado
2. **Es EN VUELO**: Es IN_TRANSIT de día anterior sin confirmar llegada

### 2.2 Viajes Excluidos
1. Estado **COMPLETED**
2. Viajes con `FleetManagementEquipmentRepositioning` que **SON de tour** (tienen `id_bloque`)
3. Viajes sin ninguna acción en la jornada

### 2.3 Viajes Siempre Incluidos
1. Viajes vacíos **SUELTOS** (no tienen `id_bloque`)
2. Tours con `FleetManagementEquipmentRepositioning`
3. `RailTrailerPoolAdjustment` (tratar como cualquier otro)

---

## 3. Semáforo de Alertas

### Colores
| Color | Condición | Acción sugerida |
|-------|-----------|-----------------|
| 🟢 Verde | >2 horas para la acción | En tiempo |
| 🟡 Amarillo | <2 horas (≤120 min) | Llamar pronto |
| 🔴 Rojo | <5 minutos (≤5 min) | Llamar ahora |
| ⚪ Gris | Sin acción en jornada | No mostrar |

### Actualización
- El semáforo se actualiza en tiempo real cada 30 segundos
- Muestra cuenta regresiva hacia la próxima acción

---

## 4. Sistema de Gestión

### Estados por Viaje
| Estado | Descripción | Efecto visual |
|--------|-------------|---------------|
| **Pendiente** | Sin gestionar | Normal |
| **Contactado OK** | Llamada realizada, todo bien | Mantiene posición |
| **Retraso** | Chófer informa de retraso | Sube a máxima urgencia |
| **Sin respuesta** | No se ha podido contactar | Mantiene posición |
| **Incidencia** | Problema reportado | Sube a máxima urgencia |
| **Cargado ✓** | Confirmación de carga | Mantiene activo para descarga |
| **Descargado ✓** | Confirmación de descarga | Fila atenuada, viaje cerrado |

### Notas
- Campo de texto libre por viaje
- Persiste en localStorage

---

## 5. Gestión de Tours

### Visualización
- **ID de tour**: Ejemplo `B-5ZLHVDKXT`
- **ID de VR**: Ejemplo `113GBQJCY`
- Mostrar ambos identificadores claramente

### Sección Activa
- Si una sección está completada pero el tour continúa → mostrar siguiente sección
- Indicar visualmente a qué tour pertenece cada sección

---

## 6. Viajes "EN VUELO"

### Definición
- IN_TRANSIT con fecha de llegada anterior a hoy
- Sin confirmar llegada (no marcado como Descargado ✓)

### Visualización
- Marcados en **amarillo** al inicio de la jornada
- Siempre visibles aunque su hora original haya pasado

---

## 7. Persistencia

### localStorage
- Guardar estado de gestión por ID de VR
- Guardar notas por viaje
- Clave: `trafico_YYYYMMDD` (una por fecha)

### Estructura
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

### Botones
- **Nueva jornada**: Limpia todos los datos y empezar desde cero
- **Indicador de guardado**: Muestra "✓ guardado" al persistir

---

## 8. KPIs en Tiempo Real

| Métrica | Descripción |
|---------|-------------|
| Total | Viajes incluidos en la jornada |
| 🟢 En tiempo | Verde + Amarillo |
| ⏳ Sin confirmar | Acciones ya pasadas sin gestionar |
| ✓ Confirmados | Cargado ✓ o Descargado ✓ |

---

## 9. Interfaz de Usuario

### Pestañas
1. **Seguimiento** - Vista completa con todas las columnas
2. **Agenda** - Vista ordenada por urgencia de llamada

### Columnas
- ID (tour + VR)
- Conductor
- Empresa
- 🕐 Horario (carga → descarga)
- Semáforo
- Gestión
- Notas

### Funcionalidades
- Ordenación por columna
- Filtro por color de semáforo
- Filtro por estado de gestión
- Búsqueda por conductor o ID

---

## 10. Entrada de Datos

### Carga de JSON
- El dashboard puede:
  1. **Leer archivo JSON local** (input file)
  2. **Arrastrar y soltar** archivo JSON

### Validaciones
- Si no hay datos → mostrar mensaje instructivo
- Si formato inválido → mostrar error claro

---

## 11. Resumen de Arquitectura

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  CSV Files  │ → │  Fase 1     │ → │    JSON     │
│  (Amazon)   │    │  Processor  │    │  Normalized │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                             ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Dashboard  │ ←  │  Filtros    │ ←  │    JSON     │
│  HTML/JS    │    │  Jornada    │    │  Input      │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 12. Estilo Visual

### Colores de Empresa
- ACELC: Rosa
- AVNHE: Azul
- AVNHE: Verde
- Otros: Gris

### Indicadores
- "⏳ CARGA hace X min" - cuando acción pasada
- "⚠️ Sin confirmar" - en rojo si sin gestionar
- "🔗 B-XXXXXXX" - enlace azul para tours
