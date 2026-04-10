# Module: Patient Vitals

## Name
patient-vitals

## Purpose
Owns all functionality related to patient vital sign data: ingestion, storage, retrieval, alerting, and trend analysis.

## Owner
Backend Engineer (primary), Data Engineer (pipeline), Frontend Engineer (dashboard)

## Boundaries

### Owns
- Vitals data ingestion (API and manual entry)
- Vitals data storage (PostgreSQL vitals table)
- Vitals data retrieval (REST API)
- Alert rule evaluation
- Vitals trend calculation
- Real-time WebSocket broadcast

### Does NOT Own
- Patient records (patient-module)
- User authentication (auth-module)
- Alert delivery (notification-module)
- Report generation (reporting-module)

## API Surface

### Endpoints
```
POST   /api/v1/vitals                  — Ingest vital signs
GET    /api/v1/vitals/:patientId       — Get latest vitals for patient
GET    /api/v1/vitals/:patientId/history — Get vitals history (paginated)
POST   /api/v1/vitals/batch            — Batch upload vitals (CSV)
GET    /api/v1/vitals/:patientId/trends — Get trend analysis

POST   /api/v1/alert-rules             — Create alert rule
GET    /api/v1/alert-rules/:patientId  — Get rules for patient
PUT    /api/v1/alert-rules/:ruleId     — Update alert rule
DELETE /api/v1/alert-rules/:ruleId     — Delete alert rule

WS     /ws/vitals/:patientId           — Real-time vitals stream
```

## Data Model

```sql
CREATE TABLE vitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id),
    vital_type VARCHAR(50) NOT NULL,  -- heart_rate, blood_pressure_sys, blood_pressure_dia, spo2, temperature
    value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,        -- bpm, mmHg, %, °F
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50) NOT NULL,      -- device, manual, batch
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vitals_patient_time ON vitals(patient_id, recorded_at DESC);
CREATE INDEX idx_vitals_type ON vitals(vital_type);

CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id),
    vital_type VARCHAR(50) NOT NULL,
    condition VARCHAR(10) NOT NULL,   -- gt, lt, gte, lte
    threshold DECIMAL(10,2) NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    severity VARCHAR(20) NOT NULL DEFAULT 'warning',  -- warning, critical
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

## Dependencies
- **auth-module**: JWT validation for API access
- **patient-module**: Patient existence validation
- **notification-module**: Alert delivery (async, via event)

## Test Strategy
- **Unit tests**: Vital sign validation logic, alert rule evaluation, trend calculation
- **Integration tests**: API endpoints (CRUD, pagination, filtering), WebSocket connection
- **E2E tests**: Manual vitals entry → dashboard display → alert trigger → acknowledgment
- **Performance tests**: 10,000 concurrent WebSocket connections, 1,000 vitals/second ingestion

## Status
Candidate (identified during BMAD analysis)
