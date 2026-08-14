# Security policy

## Supported version

Security fixes target the latest revision on `main`; no released long-term-support version currently
exists.

## Reporting a vulnerability

Do not open a public issue containing credentials, personal data, exploitable IAM details, or a
food-safety bypass. Use GitHub private vulnerability reporting when enabled on the repository. If it
is unavailable, contact the repository owner privately through the verified contact on their GitHub
profile and include a minimal sanitized reproduction.

Expected first acknowledgement: within five business days. Severity, remediation, and disclosure
timing will be coordinated after validation. Never test against an AWS account or data you do not own
or have explicit permission to assess.

The reference effect adapters do not process real payment, dispatch, or notification operations.
Using them as if they did is a deployment/configuration error, not a supported production mode.

