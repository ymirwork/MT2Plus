---
name: git-workflow
description: >-
  Automate and standardize Git and GitHub workflows: conventional commits (feat, fix, refactor, chore),
  safe branch management, merge conflict resolution, pull request drafting, release tagging (SemVer),
  changelog generation, and repository hygiene. Use for commit creation, branch operations, PRs, or release prep.
---

# Git & GitHub Workflow Standard

## 1. Conventional Commits Standard
Every commit message must follow the Conventional Commits specification:
```text
<type>(<optional-scope>): <short description in present tense>

[optional body explaining 'why' and architectural motivation]

[optional footer(s), e.g. Closes #123, Breaking Changes]
```

### Commit Types
- `feat:` Net-new feature or gameplay mechanic.
- `fix:` Bug fix, crash prevention, or regression repair.
- `refactor:` Code refactoring that neither fixes a bug nor adds a feature.
- `perf:` Performance optimization (FPS, memory allocation, network traffic).
- `docs:` Documentation updates, changelogs, or `PROJECT_CONTEXT.md` edits.
- `style:` Formatting, whitespace, semicolon fixes (no code logic changes).
- `chore:` Build scripts, package updates, dev tools, or gitignore adjustments.

### Hygiene Rules
1. **Never commit secrets:** Check `.env`, credentials, OAuth tokens, private keys before staging.
2. **Never blindly `git add .`:** Always inspect `git status` first. Stage specific files (`git add path/to/file`).
3. **Unity Engine Rule:** Whenever adding/modifying/renaming an asset in `Assets/`, **always** stage its corresponding `.meta` file in the same commit. Never commit `Library/`, `Temp/`, `Logs/`, or `obj/`.
4. **Metin2 / C++ Rule:** Do not commit temporary binaries, object files, `.data` dumps, or logs (`syserr.txt`, `dist/`).

---

## 2. Branching & Safe Merge Strategy
- **Main / Production (`main`):** Stable, tested releases only.
- **Development (`dev`):** Daily integration branch.
- **Topic Branches (`feature/<name>`, `fix/<name>`):** Isolated work.
- **Workflow:**
  1. Pull latest upstream/main: `git fetch origin`
  2. Create clean branch: `git checkout -b feature/my-feature`
  3. Work & stage surgically.
  4. Merge back cleanly (or squash if requested).

---

## 3. Pull Request (PR) Drafting Template
When preparing a PR on GitHub, format the description cleanly:
```markdown
## 📝 Summary
Brief 1-3 sentence summary of what this PR introduces and why.

## 🛠️ Changes
- **Component A:** [Detailed bullet point]
- **Component B:** [Detailed bullet point]

## 🧪 Verification & Test Plan
- [ ] Manual test in-game / editor
- [ ] No regression errors in log files (`syserr` / Unity console)
- [ ] Clean build across target platform(s)
```

---

## 4. Releases & Semantic Versioning (SemVer)
- Version pattern: `v<MAJOR>.<MINOR>.<PATCH>` (e.g. `v2.40.1` or `v2.40.0-mod62`).
- To view commits since the previous release tag:
  ```bash
  git log <last_tag>..HEAD --oneline
  ```
- Generate changelog grouped by `feat`, `fix`, and `perf`.
- Tag creation:
  ```bash
  git tag -a v2.40.1 -m "Release v2.40.1: [Summary]"
  git push origin v2.40.1
  ```
