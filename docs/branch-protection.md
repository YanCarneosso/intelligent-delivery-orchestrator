# Recommended `main` branch protection

Configure a GitHub ruleset for `main`:

- Require pull requests with at least one approval; dismiss stale approvals after new commits.
- Require review from CODEOWNERS and resolution of all conversations.
- Require the `quality` and `infrastructure` CI jobs and a merge-base-up-to-date branch.
- Block force pushes, deletions, and direct pushes; include administrators unless emergency policy
  explicitly says otherwise.
- Require signed commits or vigilant mode where the organization supports it.
- Enable secret scanning, push protection, Dependabot alerts, and dependency review.
- Protect production deployment through a GitHub Environment with reviewer approval and scoped OIDC
  role; do not store long-lived AWS keys in repository secrets.

Release tags should be immutable. Emergency bypasses must create an auditable incident/change record
and receive retrospective review.

