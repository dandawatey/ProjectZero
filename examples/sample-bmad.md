# BMAD: HealthTracker Pro

## Business Model Canvas

### Key Partners
- Cloud infrastructure (AWS/GCP)
- Medical device manufacturers (vital sign monitors)
- EHR/EMR system providers (Epic, Cerner)
- Payment processor (Stripe)
- Compliance auditor (SOC2, HIPAA)

### Key Activities
- Develop and maintain the platform
- Onboard healthcare providers
- Maintain HIPAA compliance
- Process and store vitals data securely
- Provide real-time alerting

### Key Resources
- Engineering team (5 full-stack, 1 data, 1 DevOps)
- HIPAA-compliant cloud infrastructure
- Medical domain expertise (advisor)
- Security and compliance team

### Value Propositions
- Real-time patient vital sign monitoring from anywhere
- Configurable alerts for abnormal values
- HIPAA-compliant data storage and transmission
- Integration with existing hospital systems
- Reduction in manual monitoring labor by 60%

### Customer Relationships
- Self-service onboarding for small clinics
- Dedicated onboarding for hospitals (50+ beds)
- 24/7 support for P1 issues (patient safety)
- Quarterly business reviews for enterprise

### Channels
- Web application (primary)
- Mobile app (iOS, Android) — Phase 2
- API for EHR integration
- Direct sales for enterprise

### Customer Segments
- Primary: Healthcare providers (clinics, hospitals)
- Secondary: Home health agencies
- Tertiary: Clinical research organizations

### Cost Structure
- Cloud infrastructure: $15K/month at scale
- Engineering team: $120K/month
- Compliance: $5K/month
- Support: $10K/month

### Revenue Streams
- Per-seat subscription: $49/seat/month (Standard), $99/seat/month (Enterprise)
- Data storage overage: $0.10/GB/month above 100GB
- API access: $199/month for EHR integration
- Professional services: $200/hour for custom integration

## Target Users

### Persona 1: Dr. Sarah Chen (Provider)
- Role: Attending physician, internal medicine
- Age: 42, tech-comfortable
- Goals: Monitor patients remotely, reduce hospital readmissions
- Pain points: Currently relies on nurses to call with vitals, delayed awareness
- Success: Real-time dashboard, alerts on phone, 50% faster response to deterioration

### Persona 2: Nurse James Wilson (Daily User)
- Role: Floor nurse, 12-hour shifts
- Age: 34, moderate tech skills
- Goals: Efficient vitals documentation, quick alert response
- Pain points: Manual vitals recording, paperwork, delayed escalation
- Success: Auto-capture from devices, one-click escalation, reduced paperwork by 70%

## Technical Constraints
- HIPAA compliance (mandatory, non-negotiable)
- SOC2 Type II certification (required by enterprise customers)
- Data residency: US-only for healthcare data
- Uptime: 99.99% for real-time monitoring
- Latency: < 5 seconds for vital sign display
- Data retention: 7 years (regulatory)

## Success Metrics
- North star: Number of active monitored patients
- KPIs: 1,000 providers onboarded in 12 months, 99.99% uptime, < 5s vitals latency, NPS > 50
- Leading indicators: Trial-to-paid conversion > 30%, weekly active providers > 60%

## MVP Scope
### In Scope
- Web dashboard for vitals monitoring
- Patient management (CRUD)
- Real-time vitals ingestion (heart rate, BP, SpO2, temperature)
- Configurable alert rules per patient
- User authentication with RBAC
- Audit logging for compliance
- Basic reporting (vitals trends, alert history)

### Out of Scope (Phase 2+)
- Mobile app
- EHR integration
- Predictive analytics
- Multi-facility management
- Telehealth video
- Billing and insurance
