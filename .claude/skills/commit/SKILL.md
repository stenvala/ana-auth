---
name: commit
description: Review staged changes and create well-formatted commit messages
---

# Write and Execute Commit Messages

Review staged changes and create well-formatted commit messages.

## When to Use

- Ready to commit staged changes
- Need help writing a commit message
- Want to review what will be committed

## Important

**This command does not stage files.** You must stage your changes first with `git add`.

## Instructions

### Step 1: Verify Staged Changes

```bash
git diff --cached --name-only
```

If no files are shown, stage changes first with `git add`.

### Step 2: Analyze Changes

```bash
git diff --cached
```

Review the detailed diff to understand what changed.

### Step 3: Determine Commit Details

1. **Type** - feature, fix, refactor, docs, test, chore, perf, style, ci
2. **Scope** - What area of the codebase is affected
3. **Subject** - One-liner describing the change
4. **Body** (if needed) - Explanation of what and why

### Step 4: Suggest Commit Message

Format:
```
<type>(<scope>): <subject>

<body>
```

Example:
```
feat(auth): add JWT token refresh mechanism

Tokens now refresh automatically when approaching expiration.
This prevents unauthorized errors during long operations.
```

### Guidelines

- Use simple, direct language
- State what changed and why
- Avoid words like "comprehensive", "robust", "powerful", "enhance"
- Don't describe the change as "improved" unless it replaces something
- Be specific about behavior, not quality

### Step 5: Request Approval

Present the suggested message and ask for approval:
- **Approve** - Proceed with commit
- **Modify** - Change the message
- **Discard** - Cancel and make different changes

