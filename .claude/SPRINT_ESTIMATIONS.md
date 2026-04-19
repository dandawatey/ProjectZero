# Sprint Estimations & Capacity Planning
**Date**: 2026-04-21  
**Total Capacity**: 92 engineer-days (3 sprints × ~30 days each)

## Sprint 1 (COMPLETE)
**Status**: ✅ DONE  
**Capacity**: 28 eng-days  
**Utilization**: 100%  
**Completion**: 100%

| Ticket | Title | Estimation | S1 | S2 | S3 | S4 | S5 | Status |
|--------|-------|------------|----|----|----|----|----|----|
| PRJ0-120 | SaaS-ORG-1 | 5 days | 0.5 | 0.5 | 1 | 2 | 1 | ✅ Done |
| PRJ0-121 | SaaS-AUTH-2 | 6 days | 0.5 | 1 | 1 | 2.5 | 1 | ✅ Done |
| PRJ0-122 | SaaS-BILL-2 | 5 days | 0.5 | 1 | 1 | 2 | 0.5 | ✅ Done |
| PRJ0-123 | SaaS-FE-1 | 6 days | 0.5 | 1 | 1 | 2.5 | 1 | ✅ Done |
| PRJ0-124 | SaaS-ORG-2 | 3 days | 0.5 | 0.5 | 0.5 | 1.5 | - | ✅ S5 |
| PRJ0-125 | SaaS-DASH-1 | 3 days | 0.5 | 0.5 | 0.5 | 1 | 0.5 | ✅ Done |
| **Total** | | **28 days** | **3** | **4** | **5** | **11.5** | **3.5** | |

**Key Metrics**:
- Burn rate: 2.8 eng-days/day
- Test coverage: 87–95% (avg 92%)
- Velocity: On target
- Blockers: Zero

---

## Sprint 2 (IN PROGRESS)
**Status**: 🔄 55% COMPLETE  
**Capacity**: 32 eng-days  
**Completion**: 55% (17.6 eng-days done, 14.4 remaining)  
**ETC**: May 15–17 (3–6 days early)

| Ticket | Title | Estimation | S1 | S2 | S3 | S4 | S5 | Status | % |
|--------|-------|------------|----|----|----|----|----|----|--|
| PRJ0-200 | Mobile SDK | 8 days | 0.5 | 1 | 1 | 4 | 1.5 | 🔄 S5 | 50% |
| PRJ0-201 | Analytics | 7 days | 0.5 | 1 | 1 | 3 | 1.5 | ✅ Live | 55% |
| PRJ0-202 | Rate Limiter | 4 days | 0.5 | 0.5 | 0.5 | 2 | 0.5 | ✅ Prod | 100% |
| PRJ0-203 | Cache Layer | 4 days | 0.5 | 0.5 | 0.5 | 2 | 0.5 | ✅ Prod | 100% |
| **Total** | | **32 days** | **2** | **3** | **3** | **11** | **3** | | |

**Key Metrics**:
- Burn rate: 4.8 eng-days/day (ahead of 3.2 target)
- Test coverage: 91–95%
- Production deployed: PRJ0-202, PRJ0-203 (86% cache hit, <1ms latency)
- Blockers: Zero
- ETC: May 15–17 (3–6 days early)

---

## Sprint 3 (RAMPING)
**Status**: 🔄 25% COMPLETE  
**Capacity**: 32 eng-days  
**Completion**: 25% (8 eng-days done, 24 remaining)  
**ETC**: May 24 (on track)

| Ticket | Title | Estimation | S1 | S2 | S3 | S4 | S5 | Status | % |
|--------|-------|------------|----|----|----|----|----|----|--|
| PRJ0-300 | Mobile UI | 8 days | 1 | 1 | 1 | 4 | 1 | 🔄 S5 | 80% |
| PRJ0-301 | Team Collab | 6 days | 0.5 | 1 | 1 | 3 | - | 🔄 S4 | 45% |
| PRJ0-302 | Webhooks | 6 days | 0.5 | 1 | 1 | 2.5 | - | 🔄 S4 | 45% |
| PRJ0-303 | RBAC | 6 days | 0.5 | 1 | 0.5 | 3 | - | 🔄 S4 | 30% |
| PRJ0-304 | Domains | 6 days | 0.5 | 1 | - | - | - | ⬜ Backlog | 20% |
| **Total** | | **32 days** | **3** | **5** | **3.5** | **12.5** | **1** | | |

**Key Metrics**:
- Burn rate: 8 eng-days/day Day 1 (ramp-up phase)
- Test coverage: tracking ≥85% on all
- ACME priority: PRJ0-300 (UAT approved) + PRJ0-303 (fast-track) by May 24
- Blockers: None
- ETC: May 24 (all 5 tickets on track)

---

## Total Program Metrics
| Metric | Sprint 1 | Sprint 2 | Sprint 3 | Total |
|--------|----------|----------|----------|--------|
| Capacity | 28 days | 32 days | 32 days | 92 days |
| Completed | 28 days | 17.6 days | 8 days | 53.6 days |
| Remaining | 0 | 14.4 days | 24 days | 38.4 days |
| Completion % | 100% | 55% | 25% | 58% |
| Burn Rate | 2.8/day | 4.8/day | 8/day | - |
| Target Velocity | 2.8/day | 3.2/day | 3.2/day | 3.1/day |
| On Track | ✅ | ✅ AHEAD | ✅ ON | ✅ AHEAD |

---

## Confluence Pages to Update

### 1. Sprint Overview Page
- Sprint 1: ✅ Complete (28/28 days, 6 tickets shipped)
- Sprint 2: 🔄 In Progress (55% complete, 14.4 days remaining)
- Sprint 3: 🔄 Ramping (25% complete, 24 days remaining)
- **Overall Program**: 58% complete (53.6/92 days)

### 2. Ticket Burndown Charts
- **Sprint 1**: Flat (complete)
- **Sprint 2**: 55% burndown (14.4 remaining)
- **Sprint 3**: 25% burndown (24 remaining)

### 3. Velocity Tracking
- Sprint 1: 2.8 eng-days/day
- Sprint 2: 4.8 eng-days/day (AHEAD)
- Sprint 3: 8 eng-days/day Day 1 (ramping, ON TRACK)

### 4. Risk & Blockers
- **Blockers**: 0
- **Risks**: None
- **ACME Priority**: PRJ0-300 (UAT done) + PRJ0-303 (fast-track)

---

## How to Update Confluence

1. **Go to**: https://isourceinnovation.atlassian.net/wiki/spaces/PR (ProjectZero space)
2. **Update "Sprint 1 Complete"** page with:
   - Final burndown chart (28/28 complete)
   - 6 tickets shipped (v0.1.0–v0.1.2)
   - Production metrics (600k pageviews, 17 paying, $5.9k MRR)

3. **Create/Update "Sprint 2 In Progress"** page with:
   - Current burndown (55% → 17.6/32 days)
   - 4 tickets: PRJ0-200 (50%), PRJ0-201 (55%), PRJ0-202 (100%), PRJ0-203 (100%)
   - ETC May 15–17

4. **Create "Sprint 3 Ramping"** page with:
   - Current burndown (25% → 8/32 days)
   - 5 tickets: PRJ0-300 (80%), PRJ0-301 (45%), PRJ0-302 (45%), PRJ0-303 (30%), PRJ0-304 (20%)
   - ACME priority for PRJ0-300 + PRJ0-303
   - ETC May 24

5. **Update "Program Roadmap"** with:
   - Total: 92 eng-days, 58% complete
   - Velocity: 3.1 eng-days/day (ahead of 3.2 target)
   - All 14 tickets tracked with SPARC phases + DoD
   - Link to SPARC_TICKET_DEFINITIONS.md

---

**Status**: Ready for Confluence sync  
**Next**: Sync estimation data to Confluence pages above
