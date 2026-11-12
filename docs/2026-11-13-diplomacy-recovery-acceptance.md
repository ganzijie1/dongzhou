# Diplomacy recovery acceptance (complete90)

The real four-service diplomacy path was accepted without API interception on
2026-11-13. The run reused the original durable task after transient AINPC Redis
timeouts; it did not create a replacement task or advance the game clock while
the task was active.

## Result

- Task: `63812cc5-61fa-52c0-88b1-ce47b1e3a871`
- orgFlow terminal result: `SUCCESS`
- Player settlement review: accepted
- Cloud lobbying outcome: `accepted`
- Alliance gate: authorized
- Cloud reload: verified
- Evidence: `output/integration-validation/live-diplomacy-acceptance-formal-diplomacy-complete90.json`
- Screenshot: `output/integration-validation/live-diplomacy-acceptance-formal-diplomacy-complete90.png`

The validated path was knowledge-jizhan evidence, AINPC council, NexusKernel
diplomacy mandate, orgFlow execution and NPC confirmation, player settlement
review, cloud lobbying reconciliation, and the alliance gate.

## Recovery behavior

AINPC persisted delivery callbacks and their organization-delivery effects
before the transient Redis acknowledgement failures. Its rotating effect queue
later replayed those idempotent effects and advanced the same orgFlow task from
member response through execution, result submission, manager confirmation, and
terminal settlement.

The browser acceptance now polls a timed-out schedule generation once more and
then reads the committed plan, resumes an existing remote organization task by
ID, avoids game-month advancement while the task is active, and allows a
configurable terminal wait (30 minutes by default). These rules prevent a slow
real-service recovery from being mistaken for a failed task.

orgFlow image `org-flow-engine:dongzhou-local-complete88` also excludes locally
deferred execution-deadline task IDs from the next bounded scan. A repeatedly
contended old deadline therefore cannot consume the scan limit and starve a
newer due task.
