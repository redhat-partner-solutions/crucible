# Contributing to Crucible

All contributions are valued and welcomed, whether they come in the form of code, documentation, ideas or discussion.
While we have not applied a formal Code of Conduct to this, or related, repositories, we require that all contributors
conduct themselves in a professional and respectful manner.

## Issues

The easiest way to contribute to Crucible is through Issues. This could be by making a suggestion, reporting a
bug, or helping another user.

### Suggestions

To make a suggestion open an Issue in the GitHub repository describing what feature/change you think is needed, why, and
if possible give an example.

### Bug Reports

> ❗ _Red Hat does not provide commercial support for the content of this repo. Any assistance is purely on a best-effort basis, as resource permits._

If you encounter a bug then carefully examine the output. If you choose to open an issue then please include as much
information about the problem as possible as this gives the best chance someone can help. We suggest:

- A description of your target environment
- A copy of your inventory
- Verbose Ansible logs (`-v[v[v[v]]]`)

**This may include data you do not wish to share publicly.** In this case a more private forum is suggested.

## Workflow

The required workflow for making a contribution is Fork-and-Pull. This is well documented elsewhere but to summarise:

1. Create a fork of this repository.
1. Make and test the change on your fork.
1. Submit a Pull Request asking for the change to be merged into the main repository.

How to create and update a fork is outside the scope of this document but there are plenty of
[in-depth](https://gist.github.com/Chaser324/ce0505fbed06b947d962)
[instructions](https://reflectoring.io/github-fork-and-pull/) explaining how to go about it.

All contributions should must have as much test coverage as possible and include relevent additions and changes to both
documentation and tooling. Once a change is implemented, tested, documented, and passing all checks then submit a Pull
Request for it to be reviewed.

## Peer review

At least two maintainers must "Accept" a Pull Request prior to merging a Pull Request. No Self Review is allowed. The
maintainers of Crucible are:

- Micky Costa (nocturnalastro)
- Arnaldo Hernandez (arjuhe)
- Charlie Wheeler-Robinson (crwr45)
- Marek Kochanowski (mkochanowski)

All contributors are strongly encouraged to review Pull Requests. Everyone is responsible for the quality of what is
produced, and review is also an excellent opportunity to learn.

## Commits and Pull Requests

A good commit does a *single* thing, does it completely, concisely, and describes *why*.

The commit message should explain both what is being changed, and in the case of anything non-obvious why that change
was made. Commit messages are something that has been extensively written about so need not be discussed in more detail
here but contributors should follow [these seven rules](https://chris.beams.io/posts/git-commit/#seven-rules) and keep
individual commits focussed.

A good Pull Request is the same; it also does a *single* thing, does it completely, and describes *why*. The difference
is that a Pull Request may contain one or more commits that together prepare for and deliver a feature.

Instructions on how to restructure commits to create a clear and understandable set of changes is outside the scope of
this document but it's a useful skill and there are [many](https://thoughtbot.com/blog/autosquashing-git-commits)
[guides](https://git-scm.com/docs/git-rebase) and [approaches](https://nuclearsquid.com/writings/git-add/) for to do it.

## Style Guidelines

- Favour readability over brevity in both naming and structure
- Document the _why_ with comments, and the _what_ with clear code
- As far as Ansible allows, encapsulate
