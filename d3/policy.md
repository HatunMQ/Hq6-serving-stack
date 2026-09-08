# Resource Policy

Serving is guaranteed first because it is the customer-facing endpoint; batch jobs may burst when resources are free, and batch is throttled first when the node is under pressure. Dashboard receives small burstable resources because it is spiky but not critical.

## Serving

```yaml
resources:
  requests:
    cpu: 2
    memory: 2Gi
  limits:
    cpu: 2
    memory: 2Gi

Batch
resources:
  requests:
    cpu: 500m
    memory: 256Mi
  limits:
    cpu: 1
    memory: 512Mi


dashboard
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
