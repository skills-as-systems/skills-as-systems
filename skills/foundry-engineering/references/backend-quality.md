# Backend quality: what a well-built service looks like

Use at G2 (contract), G7 (review) and G8 (claims). It points at the checks a reviewer can actually do. Deeper detail lives in `interfaces-and-services.md`, `data-and-migrations.md`, `security-engineering.md`, `reliability-and-incidents.md` and `testing-and-evidence.md`. The contract and the repo's constitution win when they disagree with this page.

## The backend pass (before G7)
1. Boundaries validate. Every input from outside (HTTP, queue, file, env) is checked for type, size and range at the edge, and rejected with a clear error. Internal code trusts validated data.
2. Errors are designed. One error shape across the API (code, message, request id), the right status codes, no stack traces or internals leaked, no swallowed exceptions, retries only for safe operations and with limits.
3. Authorisation on every route and object, not just authentication. Test that user A cannot read or change user B's data. Secrets from the environment or a vault, never in code or logs.
4. Data stays correct. Constraints in the database (not only in code), transactions around multi-step writes, migrations that can be rolled back or are expand-then-contract, no destructive change without a recovery step in the contract.
5. Idempotency where repeats happen. Payment, email and webhook handlers survive being called twice. Use idempotency keys or natural uniqueness.
6. Timeouts everywhere. Every outbound call has a timeout; list endpoints paginate; no N+1 queries in a loop; slow work goes to a job with a status.
7. You can see it. Structured logs with a request id, no personal data in logs, a health check, metrics or at least counters for errors and latency on the main paths.
8. Contract tests for the public surface. The API's documented behaviour (including errors) has tests that fail if it changes. Changing a public shape needs a compatibility note in the contract.
9. Config and deploy are boring. Same code path in every environment, config from env, a one-command local run, a rollback written down.

## Stack notes (load the one that matches)
- Node/TypeScript: strict types, schema validation at the edge (a validator library), async errors handled in one middleware, no unhandled promise rejections, `AbortSignal` timeouts on fetch.
- Python: type hints on public functions, validation models at the edge, context managers for resources, explicit transactions, no bare `except`.
- SQL: parameterised queries only, indexes for the queries you wrote, `EXPLAIN` on anything that scans a big table.
- Existing repo conventions beat these notes. Match the codebase.

## Evidence
Label each item TESTED (a test or command ran), OBSERVED (you read the code or saw output), INFERRED, or UNVERIFIED. "Looks fine" is not evidence. Run `foundry_check.py test-weakening` and `scope-drift` before G7.
