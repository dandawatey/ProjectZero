# JIRA Story: HEALTH-42

## Summary
Vitals Dashboard: Real-time patient vital signs display

## Type
Story

## Epic
HEALTH-1: Patient Vitals Module

## Description
As a healthcare provider, I want to see a patient's vital signs dashboard so that I can monitor their health status in real-time and respond quickly to deterioration.

The dashboard should display the last 24 hours of vital sign data with automatic updates.

## Acceptance Criteria
1. Dashboard shows the 4 primary vital signs: Heart Rate, Blood Pressure, SpO2, Temperature
2. Each vital sign displays: current value, unit, trend arrow (up/down/stable), mini chart (last 24h)
3. Values update automatically every 30 seconds via WebSocket
4. Abnormal values are color-coded: yellow for warning, red for critical
5. Thresholds for color-coding:
   - Heart Rate: warning < 50 or > 100, critical < 40 or > 120
   - Blood Pressure (systolic): warning < 100 or > 140, critical < 90 or > 160
   - SpO2: warning < 95%, critical < 90%
   - Temperature: warning > 99.5°F, critical > 101.3°F
6. Dashboard loads in < 2 seconds
7. WebSocket reconnects automatically on connection loss
8. Works on Chrome, Safari, Firefox (latest 2 versions)

## Story Points
5

## Priority
P1 (Critical path — core product value)

## Labels
patient-vitals, frontend, websocket, dashboard

## Technical Notes
- Use WebSocket (not polling) for real-time updates
- Chart library: Chart.js or Recharts (confirm with architect)
- Use design system components from packages/ui
- Consume types from product repo .claude/contracts/frontend-types.ts
- Responsive: works on tablet (primary use case) and desktop

## Test Approach
- **Unit**: Data transformation functions (vitals → chart data), threshold evaluation
- **Integration**: WebSocket connection lifecycle, API data fetching
- **E2E**: Load dashboard → verify vitals displayed → verify auto-update → verify color coding
- **Visual**: Storybook stories for dashboard component with all vital sign states

## Dependencies
- HEALTH-40: Vitals API endpoints (backend) — must be complete
- HEALTH-41: WebSocket server setup — must be complete
- Design system initialized (packages/ui)
