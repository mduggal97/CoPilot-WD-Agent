# Kubernetes on EKS - the scale-beyond-App-Runner path

This file is a decision aid, not a Kubernetes bible. The suite's default compute
is AWS App Runner (`aws-architecture.md`) - one container, private VPN ingress,
simple deploy/rollback, no orchestration to own. This file exists for the day a
tool genuinely outgrows that shape, or a client mandates Kubernetes. It assumes
you are NOT a Kubernetes operator and is written to keep it that way as long as
possible: read the gate in s1 first, and do not read the rest of this file
until the gate says yes.

There is zero current portfolio demand for this - deliberate forward coverage,
kept lean on purpose. Do not let it become the default answer to "how do we
host this."

## Contents

1. The gate - you do not need Kubernetes until...
2. If yes - Auto Mode vs Fargate profiles vs managed node groups
3. Minimal viable recipe for one suite-shaped app
4. Deploy path - image, apply method, rollback
5. What does NOT change
6. Azure/GCP one-liner

## 1. The gate - you do not need Kubernetes until...

Read this as a checklist you want to fail. App Runner is simpler on every
axis that matters to a small consulting-built estate: no cluster to patch, no
node AMI to rotate, no YAML surface, no on-call runbook for etcd. Staying on
App Runner is the RIGHT default - only move off it when one of these is
concretely true TODAY, not hypothetically true someday.

- **Sidecars or DaemonSets are required.** App Runner runs exactly one
  container per instance. A workload that NEEDS a co-located second process
  (service-mesh proxy, node-level log shipper, per-node security agent) -
  not just a second service - can't be expressed on App Runner.
- **Websockets or long-lived connections exceed App Runner's model.** App
  Runner has no officially documented hard request-timeout number as of Sep
  2026 (**verify-current, checked 2026-09-11**: practical reports put the
  idle cutoff around 2 minutes; open questions tracked at
  https://github.com/aws/apprunner-roadmap/issues/101 and /issues/104), and
  provisioned instances are CPU-throttled between requests (`operations.md`
  s5). Occasional keep-alives are fine; a product built AROUND persistent
  bidirectional streams (live tickers, real-time collaborative editing) is
  not.
- **GPU workloads.** App Runner has no GPU instance family. Plain Bedrock
  calls from a CPU container do NOT count - that's still App Runner's shape.
- **More than roughly 8-10 services need shared platform concerns.** A
  handful of App Runner services in parallel is trivial; past that, when
  every service needs the same cross-cutting machinery (service mesh,
  uniform canary policy, shared ingress gateway), per-service CloudFormation
  duplication starts to cost more than a cluster. Treat "8-10" as when to
  start counting, not a hard trigger.
- **A client mandates Kubernetes** - a valid, non-technical reason, some
  clients standardize on EKS/AKS/GKE as platform policy regardless of need.
- **Multi-region active-active is required.** App Runner is single-region
  with no built-in cross-region failover; true active-active with shared
  state is outside its design entirely.

**The honest cost of saying yes:**

| Cost | What it means |
|---|---|
| Cluster fee | EKS control plane: $0.10/hr standard support (~$73/mo, ~$876/yr); jumps 6x to $0.60/hr (~$438/mo) if the cluster's K8s version ages into extended support (**verify-current, checked 2026-09-11**: https://www.cloudzero.com/blog/eks-pricing/, https://cloudburn.io/blog/amazon-eks-pricing). Before any node compute. |
| Node/compute cost | Nodes run 24x7 like any compute; EKS Auto Mode adds a ~12% management surcharge over standard EC2 pricing (discounted for GPU) on what it provisions (**verify-current, checked 2026-09-11**: https://cast.ai/blog/eks-auto-mode/). |
| Ops burden | Someone owns cluster version upgrades, IAM/RBAC surface, and add-on lifecycle (unless Auto Mode owns it) - a bigger incident surface than "redeploy the App Runner service." |
| Team-skills prerequisite | The team needs to read `kubectl describe`/`logs`, understand Deployment/ReplicaSet/Pod, and debug a CrashLoopBackOff - none of which App Runner requires. If nobody wants to own that skill, keep the gate closed even if a checklist item is technically true; solve the one workload's problem another way first (e.g., a standalone Fargate task) before reaching for a cluster. |

**If none of the checklist items are true: stop here, stay on App Runner.**
That is the expected outcome for essentially every tool in the portfolio.

## 2. If yes - Auto Mode vs Fargate profiles vs managed node groups

Pick the simplest compute mode that fits; do not default to hand-rolled node
groups out of habit.

| Mode | What it is | Recommend when |
|---|---|---|
| **EKS Auto Mode** | AWS runs node provisioning/scaling/lifecycle for you, using Karpenter internally as a fully managed, off-cluster service - you never install or upgrade a Karpenter controller (**verify-current, checked 2026-09-11**: https://cast.ai/blog/eks-auto-mode/; launched re:Invent 2024, now the default modern recommendation). Costs the ~12% surcharge. | **Default for a suite-shaped app.** Lowest ops burden by far - closest thing to App Runner's simplicity. |
| **Fargate profiles** | Serverless pods, no EC2 nodes to manage. No DaemonSets, but plain sidecar containers in a pod spec still work. | Pure stateless HTTP pods with no DaemonSet need. Pairs naturally with External Secrets Operator (s3), since Fargate can't run the CSI driver's DaemonSet. |
| **Managed node groups** (self-tuned, Karpenter optional) | You choose instance types and scaling; optionally self-install Karpenter. | Fallback only - a specific AMI, a GPU family Auto Mode doesn't cover, or a client policy mandating node-level control. |

**Karpenter one-liner:** the open-source node autoscaler that provisions
right-sized nodes in seconds when pods are unschedulable (vs. the older
Cluster Autoscaler's minutes). Auto Mode gives you this managed; only
self-install Karpenter if you chose managed node groups and want its
bin-packing without the surcharge.

**Recommendation: EKS Auto Mode**, unless a specific constraint above rules
it out.

## 3. Minimal viable recipe for one suite-shaped app

Assumes the app already follows the module contract (`app-architecture`) and
the App Runner hosting shape (`aws-architecture.md`) - this changes WHERE it
runs, not what it is.

**Namespace-per-app** - one namespace per suite app, mirroring "one App
Runner service per app." Never share a namespace across apps; it's the
cheapest isolation boundary Kubernetes offers.

**Deployment + Service + Ingress:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: <app-name>, namespace: <app-name> }
spec:
  replicas: 2
  selector: { matchLabels: { app: <app-name> } }
  template:
    metadata: { labels: { app: <app-name> } }
    spec:
      serviceAccountName: <app-name>-sa   # Pod Identity binding, see below
      containers:
        - name: <app-name>
          image: <ECR_REPO_URI>:<tag>     # same image the ECR pipeline builds (s4)
          ports: [{ containerPort: 8080 }]
          readinessProbe: { httpGet: { path: /health, port: 8080 }, initialDelaySeconds: 5, periodSeconds: 10 }
          livenessProbe:  { httpGet: { path: /health, port: 8080 }, initialDelaySeconds: 15, periodSeconds: 20 }
          resources:   # starting point, tune from real usage
            requests: { cpu: "250m", memory: "512Mi" }
            limits:   { cpu: "1",    memory: "1Gi" }
---
apiVersion: v1
kind: Service
metadata: { name: <app-name>, namespace: <app-name> }
spec:
  selector: { app: <app-name> }
  ports: [{ port: 80, targetPort: 8080 }]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: <app-name>
  namespace: <app-name>
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internal   # VPN parity - never internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  rules:
    - http:
        paths:
          - { path: /, pathType: Prefix, backend: { service: { name: <app-name>, port: { number: 80 } } } }
```

**Internal ALB is the load-bearing line.** `scheme: internal` preserves the
VPN-only posture `aws-architecture.md` sets for App Runner - an internal
ALB's DNS resolves only to private IPs reachable from inside the VPC
(**verify-current, checked 2026-09-11**: AWS Load Balancer Controller docs,
https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/ingress/annotations/).
Flipping it to `internet-facing` reopens the exposure `customer-hosting.md`
treats as a deliberate, reviewed decision - never do it without that review.

**Identity to AWS - EKS Pod Identity over IRSA for new EC2/Auto-Mode
workloads.** Both remain fully supported, no forced migration
(**verify-current, checked 2026-09-11**), but Pod Identity is the current
default - simpler trust policies, portable IAM roles across clusters, no
per-cluster OIDC setup. Keep IRSA only for Fargate workloads that don't yet
support Pod Identity, or a pre-migration cluster. Either way, grant the
service account's role least-privilege access to Secrets Manager and
Bedrock - no long-lived key in the container, same principle as App
Runner's instance role (`aws-architecture.md` s3.5).

**External Secrets Operator over the CSI driver - pick one, standardize.**
The CSI driver mounts secrets as files via a privileged, node-level
DaemonSet; ESO runs as a controller Deployment that syncs Secrets Manager
values into native Kubernetes Secret objects, consumed the normal
`envFrom`/`valueFrom` way. **Recommend ESO**: no DaemonSet (works on
Fargate, matches Auto Mode), and a plain Secret is what every app already
half-expects. Don't run both in one cluster (**verify-current, checked
2026-09-11**: https://aws.amazon.com/blogs/containers/leverage-aws-secrets-stores-from-eks-fargate-with-external-secrets-operator/).

**Resource requests/limits - starting points.** `250m` CPU / `512Mi` memory
request, `1` CPU / `1Gi` limit is a reasonable floor for a FastAPI+SPA
container - roughly half of App Runner's typical `1 vCPU / 2 GB` sizing
(`aws-architecture.md` s3.1); tune from real usage, same as App Runner.
**HPA basics:** a `HorizontalPodAutoscaler` targeting 60-70% CPU with
`minReplicas: 2` and `maxReplicas` sized to peak mirrors App Runner's
autoscaling config (`operations.md` s4) - move to request-based metrics
only if CPU proves the wrong signal.

## 4. Deploy path

**Image: same ECR pipeline, unchanged.** Same CodeBuild buildspec, same ECR
repo, same image the two-account pipeline already produces
(`cloudformation-pipeline.md`) - EKS is a new place to RUN the image, not a
new way to build it.

**kubectl apply vs Helm vs GitOps (Argo CD) - simplest defensible option:**

| Option | Fit |
|---|---|
| **kubectl apply** on plain YAML (s3, as-is) | Right starting point for one app on one cluster with infrequent releases. Deploy = `kubectl apply -f .` from the pipeline stage that used to call `aws apprunner start-deployment`. |
| **Helm** | Earns its keep once several near-identical app deployments exist to template - the same "no new infra per app" principle applied to K8s manifests. Not needed for a single app. |
| **GitOps (Argo CD)** | Earns its keep once enough clusters/apps exist that manual `kubectl apply` becomes a drift risk; it continuously reconciles the cluster to a git repo's declared state with an independent audit trail. For one or two apps, this is more platform than needed - the pipeline's own history is auditable enough. Revisit past a handful of EKS apps or clusters. |

**Recommendation: start with `kubectl apply` from the existing pipeline
stage.** Move to Helm when templating repeats; move to GitOps when manual
apply becomes a real drift risk. Don't adopt either preemptively.

**Rollback: `kubectl rollout undo`, not App Runner's retag pattern.** App
Runner's prod rollback moves a mutable `:latest` tag and calls
`start-deployment` because the org SCP blocks `UpdateService`
(`operations.md` s3). Kubernetes has no equivalent constraint - a Deployment
keeps revision history by default:

```
kubectl rollout undo deployment/<app-name> -n <app-name>
# or to a specific prior revision:
kubectl rollout undo deployment/<app-name> -n <app-name> --to-revision=<N>
```

Materially simpler than the App Runner retag dance - a small upside once on
EKS, not by itself a reason to move.

## 5. What does NOT change

Moving compute to EKS changes ingress/orchestration only:

- **Container build** - same Dockerfile, same multi-stage SPA+FastAPI image,
  same ECR pipeline (s4).
- **The module contract** - FCIS split, schema-per-module, per-module
  migrations (`app-architecture`) - none of it is deployment-target-specific.
- **RDS Postgres stays RDS Postgres.** Do NOT run Postgres in-cluster (no
  StatefulSet database, no in-cluster Postgres operator) - RDS already gives
  managed backups, PITR, and Multi-AZ (`operations.md` s1-s2), and
  replicating that in-cluster is a full-time job the suite isn't staffing
  for. A pod on EKS reaches the SAME shared RDS instance over the VPC, via
  the cluster's own security group instead of the App Runner VPC connector.
- **Observability posture** - same structured logging + run_id correlation
  and CloudWatch alarms (`observability.md`); only log-shipping changes (a
  sidecar/DaemonSet shipper instead of App Runner's built-in delivery).
- **Entra auth** - identity is still Microsoft Entra, JWT validation
  unchanged; only the network path moved from App Runner's
  VpcIngressConnection to an internal ALB (s3).

## 6. Azure/GCP one-liner

The same gate (s1) applies platform-independent - it is not an AWS-specific
question. **Azure**: mirror decision is Azure Container Apps (simple path)
vs AKS - see sibling reference azure-hosting.md (authored in parallel); AKS
follows the same gate, with its own managed node pool automation as the
Auto-Mode equivalent. **GCP**: mirror decision is Cloud Run vs GKE - see
sibling reference gcp-firebase.md (authored in parallel); GKE Autopilot is
the Auto-Mode equivalent once the gate opens. Don't duplicate Azure/GCP
hosting detail here - cross-link the siblings instead.

## What to remember

- **The gate is the point of this file** - stay on App Runner unless a
  concrete, present-tense requirement (s1) is real today, not hypothetical.
- **EKS Auto Mode**, **Pod Identity over IRSA**, **ESO over the CSI driver** -
  standardize each; don't run both of a pair.
- **Internal ALB (`scheme: internal`) is non-negotiable** - flipping it
  needs the same review gate as `customer-hosting.md`.
- **RDS stays RDS - never run Postgres in-cluster.**
- **`kubectl apply` first; earn Helm and GitOps later** - same "no platform
  before you need it" discipline the suite applies to CloudFormation.
- Every pricing/version claim above is dated 2026-09-11, marked
  verify-current - re-pull before quoting a number in a real design.
