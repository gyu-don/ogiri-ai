---
name: jj
description: Jujutsu (jj) version control system for daily development workflow. Use when users work with jj commands, manage changes, or sync with Git remotes (GitHub, etc). Assumes jj as primary VCS with Git for external collaboration.
---

# Jujutsu (jj) Version Control System

You are an expert in Jujutsu (jj), a next-generation version control system. The user uses jj as their primary VCS for daily development and uses Git only for syncing with external remotes like GitHub.

## Core Concepts

### Working Copy
- **Automatic tracking**: jj automatically tracks all changes in the working directory without explicit staging (`git add` not needed)
- **Working copy as commit**: The working directory is treated as a commit that auto-amends with each command
- **Current revision**: Denoted as `@` in revset syntax
- **Added files are implicitly tracked by default**; files matching ignore patterns are excluded

### Change IDs vs Commit IDs
- **Change ID**: Stable identifier that persists across rewrites (rebases, amends, etc.)
- **Commit ID**: Git-compatible hash that changes with each rewrite
- Change IDs enable stable references during interactive development

### Operation Log
- **Every jj operation is recorded** in the operation log
- **Easy undo**: Use `jj undo` to revert the last operation
- **Time travel**: View repository state at any operation with `jj log --at-op <operation>`
- **View history**: `jj op log` shows complete operation history
- **Restore to point**: `jj op restore <op-id>` restores entire repo state

### Lock-Free Concurrency
- You can run concurrent `jj` commands without corrupting the repo
- Works even across different machines
- Conflicts between concurrent operations are detected by subsequent commands

## Daily Workflow

### Creating Changes

```bash
# Create new change on top of current revision
jj new

# Create new change on top of specific revision
jj new <revision>

# Set description for current change
jj describe -m "message"
# Or interactively
jj describe

# Finalize current change and create new one
jj commit
# With message
jj commit -m "message"

# Edit specific revision (make it the working copy)
jj edit <revision>
```

**Important**: Unlike Git, you don't need `git add`. Just edit files and run `jj describe` or `jj commit`.

### Viewing History

```bash
# Show revision graph (default view)
jj log

# Show all revisions including hidden ones
jj log -r 'all()'

# Show specific revisions using revsets
jj log -r <revset>

# Show current change details
jj show

# Show diff of current change
jj diff

# Show diff of specific revision
jj diff -r <revision>

# Show status
jj st
# or
jj status
```

**Note**: Default `jj log` shows only local commits and their immediate parents. Configure visibility via `revsets.log` in settings.

### Editing Changes

```bash
# Edit specific revision (make it working copy)
jj edit <revision>

# Squash current change into parent
jj squash

# Interactive squash (select which changes to move)
jj squash -i

# Rebase current change to new destination
jj rebase -d <destination>

# Rebase specific revision
jj rebase -r <revision> -d <destination>

# Split current change into multiple commits
jj split
# Interactive split
jj split -i

# Amend current change (just edit files and describe)
# No special command needed - changes are auto-tracked
jj describe -m "updated message"
```

### Undoing Operations

```bash
# Undo last operation
jj undo

# View operation history
jj op log

# Restore to specific operation
jj op restore <operation-id>

# Recover from accidentally editing wrong commit
jj evolog  # Find last good version
jj new <good-revision>  # Create new change from good state
```

**Best practice**: Don't fear mistakes. The operation log has your back. `jj undo` is powerful and safe.

## Git Integration

### Working with Remotes

```bash
# Clone Git repository
jj git clone <url>

# Add remote
jj git remote add <remote> <url>

# Fetch from all remotes
jj git fetch

# Fetch from specific remote
jj git fetch --remote <remote>

# Push current bookmark
jj git push

# Push all bookmarks
jj git push --all

# Push specific bookmark
jj git push --bookmark <name>

# Push change (auto-creates bookmark)
jj git push --change <revision>

# Import Git refs manually (usually automatic)
jj git import

# Export to Git (usually automatic)
jj git export
```

**Important**:
- In colocated repos (default), `jj` commands auto-import/export with Git
- Push requires bookmarks, not just commits. Use `--change` or create bookmark first
- Authentication handled through Git's mechanisms

### Bookmark Management

```bash
# List bookmarks
jj bookmark list
# or
jj bookmark

# Create bookmark at current revision
jj bookmark create <name>

# Create bookmark at specific revision
jj bookmark create <name> -r <revision>

# Move bookmark to different revision
jj bookmark move <name> --to <revision>
# or
jj bookmark set <name> -r <revision>

# Delete bookmark
jj bookmark delete <name>

# Track remote bookmark
jj bookmark track <name>@<remote>
```

**Critical difference from Git**: Bookmarks don't auto-move after commits. You must explicitly move them with `jj bookmark move`.

### GitHub Workflow

Standard workflow for creating pull requests:

```bash
# 1. Fetch latest from remote
jj git fetch

# 2. Create new change based on main
jj new main

# 3. Make your changes (edit files)

# 4. Describe your change
jj describe -m "feat: add new feature"

# 5. Create bookmark for the PR
jj bookmark create my-feature

# 6. Push to remote
jj git push --bookmark my-feature

# 7. Create PR on GitHub web interface

# 8. After PR is merged, fetch updates
jj git fetch

# 9. Continue working
jj new main
```

**Syncing with upstream during development**:

```bash
# Fetch latest
jj git fetch

# Rebase your work on updated main
jj rebase -d main
```

## Revsets (Revision Selection)

Revsets are powerful expressions for selecting commits. Most commands accept revsets.

### Common Symbols

```
@           # Current working copy revision
@-          # Parent of working copy
@--         # Grandparent
@+          # Children of working copy
root()      # Virtual root commit (parent of all commits)
```

### Navigation Operators

```
x-          # Parents of x
x+          # Children of x
::x         # All ancestors of x (including x)
x::         # All descendants of x (including x)
x::y        # Descendants of x that are ancestors of y
..x         # Ancestors of x excluding root
x..         # Non-ancestors of x
x..y        # Ancestors of y excluding ancestors of x
```

### Set Operators

```
~x          # NOT x (negation)
x & y       # Intersection
x | y       # Union
x ~ y       # x AND NOT y (difference)
```

### Common Functions

**References**:
```
bookmarks()           # All bookmark heads
remote_bookmarks()    # All remote bookmark heads
tags()                # All tags
branches()            # Alias for bookmarks()
```

**Metadata**:
```
author(pattern)       # Commits by author
committer(pattern)    # Commits by committer
description(pattern)  # Commits with matching description
```

**Content**:
```
files(pattern)        # Commits modifying matching files
diff_contains(text)   # Commits with text in diff
diff_contains(text, files)  # Search text in specific files
```

**Commit types**:
```
merges()             # Merge commits
conflicts()          # Commits with conflicts
empty()              # Empty commits
```

**Traversal**:
```
ancestors(x)         # All ancestors
descendants(x)       # All descendants
parents(x)           # Direct parents
children(x)          # Direct children
heads(x)             # Commits in x with no descendants in x
roots(x)             # Commits in x with no ancestors in x
```

**Utilities**:
```
all()                # All visible commits
none()               # No commits
latest(x, n)         # N most recent commits from x
fork_point(x)        # Fork point of x from trunk
trunk()              # Default branch head (configurable)
immutable()          # Protected commits (configurable)
mutable()            # Editable commits
mine()               # Your commits
```

### Practical Examples

```bash
# View parent commit
jj log -r @-

# View all ancestors
jj log -r ::@

# View commits between main and current
jj log -r main..@

# View all branches and tags
jj log -r 'bookmarks() | tags()'

# Find commits by author and description
jj log -r 'author(*alice*) & description(*fix*)'

# Find commits modifying specific files
jj log -r 'files("src/**/*.rs")'

# Find commits with TODO in diff
jj log -r 'diff_contains("TODO")'

# View your unmerged commits
jj log -r 'mine() ~ ::main'

# View commits with conflicts
jj log -r 'conflicts()'
```

### Pattern Matching

String patterns support multiple syntaxes:
- `exact:` - Exact match
- `glob:` - Shell-style wildcards (default)
- `regex:` - Regular expressions
- `substring:` - Substring match

Add `-i` suffix for case-insensitive matching (e.g., `glob-i:`).

### Aliases

Define custom revsets in config:

```toml
[revset-aliases]
'my-feature' = 'description(glob:"feat:*")'
'my-bugs' = 'description(glob:"fix:*") & mine()'
```

## Conflict Resolution

### How jj Handles Conflicts

- **Conflicts don't block workflow**: You can continue working with unresolved conflicts
- **Conflicts are stored and tracked** in commits
- **Descendants can be rebased** even when ancestors have conflicts
- Conflicts appear as special markers in files

### Resolving Conflicts

```bash
# View commits with conflicts
jj log -r 'conflicts()'

# Resolve conflicts interactively
jj resolve

# Or edit conflict markers directly in files
# Then jj will detect resolution automatically

# Show current conflicts
jj status

# After resolving in a separate commit, squash it
jj new <conflicted-revision>
# Fix conflicts
jj squash  # Merge resolution into parent
```

### Merge Commits

Merge commits may show as "(empty)" if they're clean merges without conflict resolution - this is expected behavior. jj measures merge changes against auto-merged parents.

## Tips & Best Practices

### 1. Embrace the Operation Log
- Don't fear mistakes - everything is recorded
- Experiment freely knowing you can `jj undo`
- Use `jj op log` to understand what happened
- `--at-op` flag allows historical inspection without side effects

### 2. Use Revsets Effectively
- Learn common patterns for efficient navigation
- Create aliases for frequently used revsets
- Combine operators for powerful queries
- Use `connected()` to show intermediate commits in ranges

### 3. No Staging Area
- Just edit files and describe
- No need for `git add` or `git commit -a`
- Changes are automatically tracked
- Use `jj split -i` or `jj commit -i` for selective commits

### 4. Git Interop
- jj maintains Git compatibility automatically in colocated repos
- Mix `jj` and `git` commands if needed (prefer read-only `git` commands)
- Push requires bookmarks - use `--change` or create bookmark first
- Always run `jj git fetch` before creating PR branches

### 5. Multiple Working Copies
- Use `jj workspace add` for parallel work streams
- Run long tests in one workspace while developing in another
- Each workspace shares the same repository state

### 6. Recording Intermediate Work
- Use `jj new` to create savepoints without formal commits
- Split changes with `jj split -i` for better history
- Describe changes incrementally as you work

### 7. Monitoring History Evolution
- Pair `watch` with `jj log` for live updates:
  ```bash
  watch --color jj --ignore-working-copy log --color=always
  ```

### 8. Private Commits
- Create separate private commit branched from main
- Merge into working branch as needed
- Mark as private via `git.private-commits` config to prevent pushes

## Common Gotchas & FAQ

### Bookmarks don't move automatically
Unlike Git's HEAD, jj bookmarks don't auto-advance after commits. You must explicitly move them:
```bash
jj bookmark move my-feature --to @
```

### Can't see my commit in log
Default `jj log` shows only local commits and immediate parents. Your commit might be hidden:
```bash
jj log -r 'all()'  # Check if it exists
```
Configure default visibility in settings with `revsets.log`.

### "Elided revisions" in log output
When logging a subset, intermediate commits may not appear. Use `connected()` to show them:
```bash
jj log -r 'connected(main..@)'
```

### Push says "nothing to push"
`jj git push --all` pushes only bookmarks. To push a specific commit:
```bash
# Option 1: Auto-create bookmark
jj git push --change <revision>

# Option 2: Create bookmark manually
jj bookmark create my-feature
jj git push --bookmark my-feature
```

### Accidentally edited wrong commit
Use operation log to recover:
```bash
jj op log          # Find operation before mistake
jj undo            # Undo last operation
# Or
jj op restore <op-id>  # Restore to specific state
```

### Merge commits show as "(empty)"
This is expected for clean merges. jj measures changes against auto-merged parents. A merge without conflict resolution appears empty.

### Want to prevent working copy snapshots
Don't fight the automatic snapshotting - embrace it. Use `jj new` to create bookmarks for potential rollback points instead.

## Quick Reference: Git to jj

| Git | jj |
|-----|-----|
| `git init` | `jj git init [--no-colocate]` |
| `git clone <url>` | `jj git clone <url>` |
| `git status` | `jj st` / `jj status` |
| `git add <file>` | _(automatic)_ |
| `git commit -a` | `jj commit` |
| `git commit -m "msg"` | `jj commit -m "msg"` |
| `git commit --amend` | `jj squash` |
| `git log` | `jj log` |
| `git show` | `jj show` |
| `git diff` | `jj diff` |
| `git diff HEAD~` | `jj diff -r @-` |
| `git branch` | `jj bookmark list` |
| `git branch <name>` | `jj bookmark create <name>` |
| `git branch -d <name>` | `jj bookmark delete <name>` |
| `git checkout <rev>` | `jj edit <rev>` |
| `git checkout -b <name>` | `jj new` + `jj bookmark create <name>` |
| `git merge <rev>` | `jj merge <rev>` |
| `git rebase -i` | `jj rebase -d` + `jj squash -i` |
| `git cherry-pick` | `jj rebase -r <rev> -d @` |
| `git reset --hard` | `jj edit <rev>` |
| `git reset HEAD~` | `jj undo` |
| `git fetch` | `jj git fetch` |
| `git pull` | `jj git fetch` + `jj rebase -d main` |
| `git push` | `jj git push` |
| `git push --all` | `jj git push --all` |
| `git stash` | `jj new` (changes auto-tracked) |
| `git reflog` | `jj op log` |
| _(none)_ | `jj undo` |
| _(none)_ | `jj split` |
| _(none)_ | `jj describe` |

## Configuration Examples

### Set default revset for log
```toml
[revsets]
log = "@ | ancestors(remote_bookmarks(), 2) | trunk()"
```

### Define custom aliases
```toml
[revset-aliases]
'my-changes' = 'mine() ~ ::trunk()'
'review-needed' = 'description(glob:"feat:*") | description(glob:"fix:*")'
```

### Mark commits as private
```toml
[git]
private-commits = "description(glob:'wip:*')"
```

### Set default trunk
```toml
[revsets]
trunk = "main@origin | main"
```

## Additional Resources

- Tutorial: https://martinvonz.github.io/jj/latest/tutorial/
- Documentation: https://martinvonz.github.io/jj/latest/
- GitHub: https://github.com/jj-vcs/jj

Remember: jj is designed to be safe and easy to undo. Experiment confidently!
