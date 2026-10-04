# Hyphae Sync Integration

When the practitioner says "sync", the agent should run hyphae's pre-sync
capture before executing the git push sequence.

## Updated sync flow

1. `hyphae fruit` (or `scripts/pre-sync.sh`) - capture environment state
2. Pull latest from origin (all repos)
3. Commit any uncommitted work (all repos)
4. Push (all repos) - hyphae state travels with the push

## Why before push, not after

The fruit needs to be committed and pushed so the other machine can pull it.
If we fruit after push, the state doesn't travel until the next sync.

## Integration with existing sync command

The agent's "sync" implicit command should prepend hyphae fruit:

```
sync = hyphae_fruit() → pull all → commit all → push all
```

The fruit.yaml and any active thread YAMLs in .hyphae/ get committed
as part of the normal `git add -A && git commit` step.

## Repos that carry hyphae state

By default, hyphae state lives in whichever repo HYPHAE_REPO_ROOT points to
(or the current git root). Point it at your primary working repo.

The fruit.yaml captures state FROM all repos but LIVES in one repo.
This means only one repo needs to be pulled on the other side to get
the full environment snapshot.
