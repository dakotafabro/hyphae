# hyphae

Session continuity for AI agents across machines. Working state travels through git-synced repositories so your agent picks up exactly where you left off.

## The Problem

You're working on a feature at your desk. You close the laptop, walk to the couch, open a different machine. You start a new session. The agent has no idea what you were doing. You re-explain context. You lose momentum. The thread breaks.

Hyphae fixes this. One command captures your working state. Another command hydrates it on the other side. Git is the transport layer. No services, no accounts, no cloud sync to configure.

## The Metaphor

In mycelial networks, hyphae are the connective tissue between nodes. They translocate nutrients and chemical signals across the organism - carrying what one part of the network knows to wherever it's needed next.

This tool does the same for working state. Your machines are nodes. Git repos are the shared substrate. Hyphae carry context between them.

## Commands

### `hyphae sporulate`

Capture a single thread of working state into a compressed, portable capsule.

What gets captured:

```yaml
thread_name: offline-sync
task: Building offline-first sync for field data collection
decisions: Repository pattern with Room, not raw SQLite. Last-write-wins for v1.
open_questions: Should we queue mutations or replay them?
next_steps: Write the SyncWorker integration test
relevant_files: app/src/main/java/com/example/sync/SyncRepository.kt
context: Blocked on backend batch endpoint confirmation
timestamp: 2026-07-17T18:45:00+00:00
machine: work
session_id: a3f7b2c1
```

The capsule lands in `.hyphae/active/offline-sync.yaml`.

### `hyphae fruit`

Full environment snapshot. Captures everything - not just one thread, but the entire working state across all repos.

What gets captured:

```yaml
type: fruit
timestamp: 2026-07-17T19:00:00+00:00
machine: work
priorities: hyphae-build is primary. spore-patent is waiting.
working_memory: Just finished building fruit command. Ready to test.
threads:
  - hyphae-build
  - spore-patent
repos:
  - path: ~/notes
    branch: main
    clean: false
    dirty_files: [conventions/patent-workflow.md]
  - path: ~/development/hyphae
    branch: main
    clean: true
goose_extensions: [spore, hyphae, rpwhy, ...]
```

Fruit auto-runs when you say "sync" - captures state before the push so it travels to the other machine.

### `hyphae germinate`

Resume on another machine. If a fruit exists from another machine, presents a selective menu:

```
Found fruit from work (2h ago):

Threads:
  1. hyphae-build - Building hyphae MCP
  2. spore-patent - Patent disclosure submitted

Repos: 4 tracked (1 dirty on work side)
Extension gaps: none
Priorities: hyphae-build is primary

Which threads do you want to activate?
```

You choose what to hydrate. Not all-or-nothing.

On germination, the agent receives: what you were working on, what's decided, what's open, what to do next, which files matter. It picks up without you re-explaining.

### `hyphae primordia`

List all active threads. What's forming, not yet complete.

```
Active threads:

  hyphae-build     (work, 2h ago)    Building hyphae MCP
  spore-patent     (work, 2h ago)    Patent disclosure submitted
```

### `hyphae senescence`

Mark a thread as complete. Graceful closure. Moves to `.hyphae/history/` with a completion timestamp.

### `hyphae metrics`

Thread lifecycle stats, cross-machine transitions, germination rate. Data for correlating with rp-why and spore experiments.

```json
{
  "threads": {
    "total_created": 14,
    "currently_active": 3,
    "completed": 11,
    "avg_lifespan_hours": 28.4
  },
  "transitions": {
    "total_cross_machine": 23,
    "work_to_personal": 15,
    "personal_to_work": 8
  }
}
```

### `hyphae help`

Full command reference with natural language triggers. Accessible in-session by asking "what can hyphae do?" or "hyphae commands."

## Natural Language

You don't need to memorize command names. Say whatever feels natural:

| You say | Hyphae does |
|---|---|
| "sporulate" / "save where I am" / "package this" | sporulate |
| "fruit" / "I'm done for the day" / "switching machines" | fruit |
| "germinate" / "pick up where I left off" / "resume" | germinate |
| "what's active?" / "what's forming?" | primordia |
| "close [thread]" / "that's shipped" | senescence |
| "hyphae help" / "what can hyphae do?" | help |
| "sync" | auto-fruits, then syncs all repos |

## Sync Integration

When you say "sync", hyphae auto-fruits before push:

```
sync = fruit -> pull all -> commit all -> push all
```

The fruit travels with the push. The other machine pulls and sees fresh state on session start. The SessionStart hook fires and nudges:

```
🌿 [hyphae] 2 thread(s) from another machine ready to germinate
🌿 [hyphae] run hyphae_primordia to see active threads
```

## Germination Tagging

When a session germinates, hyphae writes a marker (`.hyphae/.last-germination.yaml` and env vars) that other instruments can read:

- `HYPHAE_GERMINATED=true`
- `HYPHAE_GERMINATED_CROSS_MACHINE=true/false`

This lets rp-why and spore segment their data by germinated vs cold-start sessions - measuring whether context continuity improves collaboration quality and retrieval efficiency.

## Installation

```bash
git clone https://github.com/dakotafabro/hyphae ~/development/hyphae
```

Add to `~/.config/goose/config.yaml`:

```yaml
  hyphae:
    enabled: true
    type: stdio
    name: hyphae
    cmd: uvx
    args:
      - --from
      - ~/development/hyphae/mcp
      - mcp_hyphae
    envs:
      HYPHAE_REPO_ROOT: ~/notes
      HYPHAE_REPOS: ~/notes:~/development/hyphae  # repos fruit captures
      AGENT_MACHINE: work  # or "personal"
    env_keys:
      - HYPHAE_REPO_ROOT
      - AGENT_MACHINE
    timeout: 300
```

Set machine identity:

```bash
echo "work" > ~/.agent-machine    # or "personal"
```

Initialize hyphae state in your working repo:

```bash
mkdir -p ~/notes/.hyphae/active ~/notes/.hyphae/history
```

## How It Works

```
Machine A (work)                    Machine B (personal)

  session active
  work happens
  decisions made

  "sync"
  > hyphae fruits (captures state)
  > repos commit and push

                                    session starts
                                    > hook detects threads from work
                                    > "germinate"
                                    > selective menu presented
                                    > agent hydrates with context
                                    > picks up seamlessly

                                    work continues
                                    new decisions made

                                    "sync"
                                    > hyphae fruits
                                    > repos commit and push

  next session
  > hook detects threads from personal
  > germinate
  > picks up where personal left off
```

## Security Model

Hyphae transports working *state* (task descriptions, decisions, next steps), not source code. The security boundary is git authentication, not hyphae.

**What git/GitHub already handles:**
- Org repos (work) are inaccessible from personal machines (SSO prevents clone/pull)
- Source code never exists on machines without auth
- Patches referencing org repos are inert on personal (no target repo to apply to)

**What hyphae adds on top:**
- Patches do not cross machines by default (`patches_cross_machine: false`). Even though they can't apply without the target repo, they're excluded from the transport to avoid carrying diffs of proprietary code in plaintext.
- Thread YAML contains task summaries and decisions at the same sensitivity level as your working repo. If your working repo is private and on both machines, hyphae doesn't increase your exposure surface.
- No credentials, tokens, or secrets should appear in thread state. The agent captures working context, not auth material.

**Policy file (optional):**

```yaml
# .hyphae/policy.yaml
policy:
  patches_cross_machine: false   # default - patches stay local
```

## Relationship to Spore

Spore is the biomimetic memory system. It handles long-term knowledge topology - decay, proximity graphs, consolidation, interoception. It answers: "What has the agent learned over time?"

Hyphae handles working state continuity. It answers: "What am I actively doing right now, and how do I resume it elsewhere?"

They complement each other:
- Spore tracks retrieval patterns across sessions. Hyphae tracks working threads across machines.
- Germination tagging lets spore compare retrieval efficiency in germinated vs cold-start sessions.
- Both live in the same repo and share session IDs as a common reference.
- Neither requires the other to function.

Integrated, not coupled.

## Directory Structure

```
.hyphae/
├── active/                  Current threads (YAML)
├── history/                 Completed threads (YAML)
├── patches/                 Dirty-state diffs (local only, don't cross machines)
├── fruit.yaml               Last full environment snapshot
├── policy.yaml              Security policy
└── .last-germination.yaml   Germination tag for rp-why/spore correlation
```

## Design Principles

1. **Git is the transport.** No external services. Push/pull is the sync mechanism.
2. **Structured YAML.** Human-readable, inspectable, diffable.
3. **Automatic hydration on session start.** The hook detects threads and nudges.
4. **Local and inspectable.** All data stays in your repos.
5. **Selective germination.** You choose what to activate.
6. **Energy conservation.** Context continuity reduces re-orientation cost (tokens, attention, time).
7. **Measurement-ready.** Germination tagging enables correlation with collaboration quality data.

## Scripts

Shell scripts in `scripts/` that support hooks and CLI usage:

| Script | Purpose |
|---|---|
| `session-start.sh` | Runs on SessionStart hook. Lists active threads and nudges the agent to germinate threads from another machine. Stays silent when a goose-banner provider matching `banner.d/*hyphae*` exists, so the threads show once. Set `HYPHAE_FORCE_BANNER=1` to always print. |
| `pre-sync.sh` | Runs before sync. Captures a fruit snapshot so working state travels with the push. |
| `help.sh` | Prints the full command reference to the terminal. |

`sync-integration.md` in the same directory documents the sync flow end-to-end.

## Testing

38 tests via pytest in `mcp/tests/`:

| File | Coverage |
|---|---|
| `test_sporulate.py` | Thread creation, YAML serialization, overwrite behavior |
| `test_germinate.py` | Selective hydration, cross-machine detection, menu presentation |
| `test_io.py` | File read/write, directory creation, history moves |
| `test_config.py` | Machine detection, env var resolution, policy loading |

Run with:

```bash
cd mcp && pytest
```

## Plugin Registration

Hyphae registers as a goose plugin via two files:

- **`plugin.json`** - Plugin metadata (name, version, description). Goose uses this for discovery.
- **`hooks/hooks.json`** - Declares the SessionStart hook, which runs `scripts/session-start.sh` to detect threads on session open.

## License

Apache 2.0
