# hyphae - what changes for you

hyphae keeps your working state when you switch machines. You save where you are, git carries it, and the agent on the other machine picks up without you re-explaining.

## What it does, and to the agent

- **sporulate** saves one thread: task, decisions, open questions, next steps, relevant files.
- **fruit** snapshots everything: priorities, threads, repo branches and dirty files, goose extensions. It runs on "sync".
- **germinate** shows threads from another machine and lets you pick which to resume.
- **primordia** lists active threads; **senescence** closes one.

At session start, a hook tells the agent when threads from another machine are waiting. You speak plainly: "save where I am", "pick up where I left off".

## When to use it

Work that spans sessions or machines. Skip it for one-off questions.

## Reserved for human judgment

You choose which threads to germinate; it isn't all-or-nothing. You also decide what's safe to write in a thread, since it travels in git.

## What it reads, writes and sends

- Writes YAML under `.hyphae/` in your working repo (`active/`, `history/`, `patches/`) and a germination marker.
- Fruit reads git status for the repos in `HYPHAE_REPOS`.
- Data leaves your machine only through your own git pushes. Patches stay local by default (`patches_cross_machine: false`).
- Threads should never hold credentials, tokens or secrets. Keep your working repo private.

## Cost

About 1,200 tokens of context (`token_cost` in bpm.json).

## Check it's working

Say "what's active?". You should see your threads with machine and age.

## Turn it off

Remove the `hyphae` entry from your goose config, then `bpm remove hyphae`. The `.hyphae/` folder stays in your repo.
