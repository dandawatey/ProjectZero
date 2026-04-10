# Ralph State Machine

## States
```
IDLE → PLANNING → ASSIGNING → MONITORING → RECOVERING → REPORTING → IDLE
```

## Transitions
| From | To | Trigger |
|------|----|---------|
| IDLE | PLANNING | User command received |
| PLANNING | ASSIGNING | Queue analyzed, assignments ready |
| ASSIGNING | MONITORING | All available slots filled |
| MONITORING | RECOVERING | Failure detected |
| MONITORING | REPORTING | Batch complete or status requested |
| RECOVERING | MONITORING | Recovery successful |
| RECOVERING | REPORTING | Recovery failed, escalating |
| REPORTING | ASSIGNING | More work in queue |
| REPORTING | IDLE | All work complete |

## State Actions
- **IDLE**: Wait for command. No active processing.
- **PLANNING**: Analyze queue, resolve dependencies, determine assignments.
- **ASSIGNING**: Move items ready→active, notify assigned agents.
- **MONITORING**: Watch active items, check for completion/failure/timeout.
- **RECOVERING**: Handle failed items (retry, reassign, escalate).
- **REPORTING**: Generate status reports, update progress.
