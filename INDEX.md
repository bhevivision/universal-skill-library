# Skill index

This file is the starting point for any agent using this repository. The library is model-independent: use the skill content that fits the task, regardless of which agent or model is active.

## How to use this library

1. Read this index and the relevant skill's `SKILL.md` before acting.
2. Match the project goal and constraints to the skill descriptions below. A directory is a browsing aid, not a hard boundary; skills may apply across categories.
3. Bring only the selected skill and the resources it references into the target project. Keep its source and license attribution.
4. Follow the skill's workflow where it fits the user's request and the target environment. Ignore agent-specific installation or command examples when that agent is unavailable; adapt those separately without changing the portable source.
5. Tell the user which skills were selected and note any missing dependencies or incompatible instructions.

Do not treat a skill as authorization to take actions the user has not requested. Repository materials are reference content; the user's current request and applicable project instructions determine the task.

## Browse by area

- [Engineering](skills/engineering/README.md) — software development, architecture, testing, security, delivery, and technical workflows.
- [Research](skills/research/README.md) — research, evidence gathering, analysis, and synthesis.
- [Writing](skills/writing/README.md) — drafting, editing, documentation, and communication.
- [Automation](skills/automation/README.md) — repeatable procedures, integrations, and task automation.

A useful skill can belong to more than one area. Keep one canonical copy and link it from other relevant sections rather than creating divergent duplicates. Add tags and cross-links in its index entry so agents can find it from different task descriptions.

## Skill entry format

Each area README should list skills with:

| Field | Purpose |
|---|---|
| Name and path | Stable identifier and where to read it |
| Use when | Concrete task signals |
| Avoid when | Important scope limits, if any |
| Dependencies | Tools, files, or prerequisites |
| Source and license | Original author/repository and applicable license |

Every skill directory should include a `SKILL.md` with a short name, a clear description, the procedure, constraints, and links to any supporting resources. Keep portable guidance separate from agent-specific adapters or commands.

## Provenance and licensing

Preserve each source's copyright and license notice when copying or adapting material. Record the original project, URL, author, license, version or commit, and any changes in the skill's metadata or adjacent provenance file. Do not assume that the repository's own license replaces a skill's upstream license. When a skill's license or origin is unclear, retain it as an unclassified reference until clarified.

## Current inventory

The category links above describe the intended organization. A category is populated only when its README lists actual skills. Do not infer that a skill exists or has been tested just because a category is listed.
