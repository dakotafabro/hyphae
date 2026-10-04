def hyphae_help_impl() -> str:
    return """
🌿 hyphae - session continuity across machines

Translocation of working state through shared substrate.

COMMANDS
────────────────────────────────────────────────────────

  sporulate    Save a single thread of working state.
               Captures: task, decisions, open questions,
               next steps, relevant files, machine origin.

               Say: "sporulate", "save where I am",
               "package this", "bookmark this"

  fruit        Full environment snapshot. Captures all
               active threads, repo states (branches,
               dirty files), goose extensions, priorities,
               and working memory. Auto-runs on sync.

               Say: "fruit", "I'm done for the day",
               "switching machines", "package everything"

  germinate    Resume on another machine. If a fruit
               exists, presents the full environment with
               selective hydration (choose which threads
               and repos to activate). If no fruit, reads
               the most recent thread.

               Say: "germinate", "pick up where I left off",
               "what was I working on?", "resume"

  primordia    List all active threads. What's forming,
               not yet complete.

               Say: "primordia", "what's active?",
               "what's forming?", "show threads"

  senescence   Mark a thread as complete. Graceful closure.
               Moves to history.

               Say: "close [thread]", "done with [thread]",
               "that's shipped", "senescence"

  help         This menu.

               Say: "hyphae help", "what can hyphae do?",
               "hyphae commands"

SYNC INTEGRATION
────────────────────────────────────────────────────────

  When you say "sync", hyphae auto-fruits before push:

    sync = fruit -> pull all -> commit all -> push all

  The fruit travels with the push. The other machine
  pulls and sees fresh state on session start.

SELECTIVE GERMINATION
────────────────────────────────────────────────────────

  When a fruit exists from another machine, germinate
  presents a menu:

    - All active threads (pick which to hydrate)
    - Repo states (branch mismatches flagged)
    - Extension gaps (what's missing on this machine)
    - Patches available (if any)
    - Priorities and working memory

  You choose what to activate. Not all-or-nothing.

DATA
────────────────────────────────────────────────────────

  All state lives in .hyphae/ at your repo root:

    .hyphae/
    ├── active/       Current threads (YAML)
    ├── history/      Completed threads (YAML)
    ├── patches/      Dirty-state diffs (local only)
    └── fruit.yaml    Last full environment snapshot

  Git is the transport. No external services.
  All files are human-readable YAML.
""".strip()
