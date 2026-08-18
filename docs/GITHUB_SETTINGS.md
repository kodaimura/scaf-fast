# GitHub Repository Settings

GitHub repository settings are not copied from a template repository. A
repository owner or administrator should complete this checklist once after the
initial push and the first successful CI run.

## Pull request settings

Open **Settings > General > Pull Requests** and configure the repository to:

- Enable squash merging.
- Disable merge commits.
- Disable rebase merging.
- Automatically delete head branches after merging.

## Main branch ruleset

Open **Settings > Rules > Rulesets**, create a branch ruleset targeting `main`,
and enable these rules:

- Require a pull request before merging.
- Require the `Test` check from the `CI` workflow to pass.
- Require conversation resolution before merging.
- Restrict branch deletion.
- Block force pushes.

Use zero required approvals for solo development. Require at least one approval
when other developers can merge changes. Set the ruleset to **Active** after
reviewing its target and bypass permissions.
