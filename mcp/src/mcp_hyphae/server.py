from fastmcp import FastMCP

from .tools.fruit import hyphae_fruit_impl
from .tools.germinate import hyphae_apply_patch_impl, hyphae_germinate_impl, hyphae_germinate_repos_impl
from .tools.help import hyphae_help_impl
from .tools.metrics import hyphae_metrics_impl
from .tools.primordia import hyphae_primordia_impl
from .tools.senescence import hyphae_senescence_impl
from .tools.sporulate import hyphae_sporulate_impl

INSTRUCTIONS = """Hyphae enables session continuity across machines. Working state is saved as structured YAML and synced via git.

WHEN TO USE EACH TOOL:

hyphae_primordia - On session start, check for active threads. If threads exist from another machine, offer to germinate.

hyphae_sporulate - When the practitioner wants to save a single thread of work. Triggers include:
  "sporulate", "save where I am", "package this", "bookmark this", "capture this thread"

hyphae_fruit - Full environment snapshot. Triggers include:
  "fruit", "I'm done for the day", "switching machines", "package everything", "sync" (auto-fruits before push)

hyphae_germinate - Resume from another machine or previous session. Triggers include:
  "germinate", "pick up where I left off", "what was I working on?", "resume", "hydrate"
  If a fruit exists from another machine, present the selective menu (threads, repos, gaps).
  If the practitioner names a specific thread, hydrate just that one.

hyphae_germinate_repos - After the practitioner selects threads, pull the associated repos.

hyphae_apply_patch - Only if patches exist and the practitioner confirms.

hyphae_senescence - Close a completed thread. Triggers include:
  "close [thread]", "done with [thread]", "that's shipped", "senescence"

hyphae_help - Show all commands and usage. Triggers include:
  "hyphae help", "what can hyphae do?", "hyphae commands", "how does hyphae work?"

WHAT EACH TOOL CAPTURES:
- Sporulate: task, decisions, open questions, next steps, relevant files, machine, timestamp.
- Fruit: all active threads + repo states (branches, dirty files) + priorities + working memory + goose extensions.
- Germinate: reads saved state and presents it for selective hydration. The practitioner chooses what to activate."""

mcp = FastMCP("hyphae", instructions=INSTRUCTIONS)


@mcp.tool()
def hyphae_help() -> str:
    """Shows all hyphae commands with descriptions and natural language triggers."""
    return hyphae_help_impl()


@mcp.tool()
def hyphae_sporulate(
    thread_name: str,
    task: str,
    decisions: str = "",
    open_questions: str = "",
    next_steps: str = "",
    relevant_files: str = "",
    context: str = "",
    handoff_effort: str = "",
) -> str:
    """Captures working state into a portable capsule for resumption on any machine.

    handoff_effort: optional slug for a page in the team handoff repo (efforts/<slug>.md).
    Leave empty for personal or local-only work; only threads with it set are shared by handoff-sync.
    """
    return hyphae_sporulate_impl(
        thread_name=thread_name,
        task=task,
        decisions=decisions,
        open_questions=open_questions,
        next_steps=next_steps,
        relevant_files=relevant_files,
        context=context,
        handoff_effort=handoff_effort,
    )


@mcp.tool()
def hyphae_fruit(
    priorities: str = "",
    working_memory: str = "",
) -> str:
    """Full environment snapshot: all active threads, repo states, dirty files, extensions, priorities. Use before sync or machine switch."""
    return hyphae_fruit_impl(
        priorities=priorities,
        working_memory=working_memory,
    )


@mcp.tool()
def hyphae_germinate(thread_name: str = "") -> str:
    """Reads saved working state. If thread_name is empty, returns the most recently modified thread."""
    return hyphae_germinate_impl(thread_name=thread_name)


@mcp.tool()
def hyphae_germinate_repos(repo_paths: str) -> str:
    """Pull latest for specified repos (comma-separated paths). Use after selecting which threads to activate."""
    return hyphae_germinate_repos_impl(repo_paths=repo_paths)


@mcp.tool()
def hyphae_apply_patch(patch_name: str) -> str:
    """Apply a saved patch file to restore dirty working state from another machine."""
    return hyphae_apply_patch_impl(patch_name=patch_name)


@mcp.tool()
def hyphae_primordia() -> str:
    """Lists all active threads - shows thread name, task summary, last updated, and origin machine."""
    return hyphae_primordia_impl()


@mcp.tool()
def hyphae_metrics() -> str:
    """Thread lifecycle stats, cross-machine transitions, germination rate. Data for correlating with rp-why and spore."""
    return hyphae_metrics_impl()


@mcp.tool()
def hyphae_senescence(thread_name: str, summary: str = "") -> str:
    """Closes a thread by moving it from active to history. Optionally records a completion summary."""
    return hyphae_senescence_impl(thread_name=thread_name, summary=summary)


def main():
    mcp.run()
