# Serverless development boundaries

This change records the concurrently merged serverless development architecture: Lambda producers, Aurora Serverless v2 PostgreSQL, a DynamoDB admission/lease control plane, versioned storage, Cognito, queues and private web hosting. It is an optional development profile. Canonical Fargate/RDS QA/prod delivery, independent QA promotion and recovery admission remain their existing implementation.

The runtime uses QA transport/authentication rules with an explicit serverless-development profile in the intended Ohio region. That alias does not establish canonical QA acceptance. Serverless production mode must refuse rather than inheriting a development-only deployment's evidence.

Stopping new Lambda invocations is insufficient to drain an invocation still initializing. Deployment must close runtime admission atomically; every producer lease acquisition must condition on that admission state/generation before any SQL. Existing leases remain visible until database connections are disposed. A closed, drained generation allows only the deliberately owned maintenance phase. Missing or incompatible deployed admission protocol cannot be treated as safe quiescence.

Maintenance receipts bind the requested operation and its exact outcome to the admitted function, role, account, configuration and source. Current trusted thirteen-job source evidence is rechecked at cloud mutation stages. Failure journals describe actual completed stages; they do not imply rollback or cancellation.

CloudFront's configured first-header/idle origin timeout is sixty seconds. A longer streaming lifetime or client deadline does not extend that bound. Cold/resumed-database transport requires genuine cloud observation before any latency qualification. Clients preserve one overall abort/deadline through refresh and stream reads. Guest exports explicitly disable serverless mode and account origins regardless of inherited cloud settings.

The existing canonical restore tools target ECS/RDS instances. A complete serverless Aurora/Lambda restore/reconciliation adapter is separate missing software; it is not described as merely an unexecuted test. Development deployment is not production promotion. Existing serverless records/journals must be retained on failure, and missing recovery evidence must not be replaced by establishing a new journal.
