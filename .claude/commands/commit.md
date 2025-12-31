---
description: Stage and commit changes with a message
argument-hint: [commit message]
allowed-tools: Bash(git status:*), Bash(git add:*), Bash(git diff:*), Bash(git commit:*)
---

Commit the current changes with message: $ARGUMENTS

1. Run `git status` to see what changed
2. Run `git add -A` to stage all changes
3. Create the commit with the provided message, adding the standard footer:

```
$ARGUMENTS

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
