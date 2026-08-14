# IAM policy mapping

IAM is generated from `template.yaml` so ARNs resolve to deployed resources. The execution role can
invoke only the five workflow Lambdas, the selected Nova Lite foundation model, and `PutItem` / 
`UpdateItem` on the idempotency table. Lambda functions can only write their own scoped log groups.

The single `Resource: "*"` exception covers CloudWatch Logs delivery control-plane APIs that do not
support resource-level permissions. It is isolated in `StepFunctionsLogDelivery` and documented in
ADR 0007.

