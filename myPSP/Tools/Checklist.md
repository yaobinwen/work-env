# Checklist

## Anti-patterns

- [ ] `Whac-A-Mole`: Only solve a problem when it arises; have not developed a permanent solution for the root cause.
  - When I was working on the unit test failures caused by incorrectly using the `libzmq.a` in the Teigha's library, I simply removed the `libzmq.a` file to avoid the problem. However, Teigha's `lib` folder has many other non-Teigha static library files which, even if they don't cause any problems now, may cause problems in the future. The **correct solution** would be to keep the Teigha library files we actually use and remove the rest.

## General Programming

- [ ] Avoid duplicating code whenever possible.
  - If duplication is inevitable, add `DUPE` or `XREF` comment to refer to the original code so others will know where to find all the copies.
  - Also add a comment to explain why the duplication is inevitable at that time, so the code reviewers will know you have already tried.
- [ ] Never lose error/exception information for debugging.
  - When catching an exception, always record the execution information (e.g., `sys.exc_info()` in Python).
  - When handling an error exit code, always record the `errno` information.
- [ ] Think from the user's perspective to write the error or help messages.
  - For example, when we say in a help message that a variable is about the "size" of something, we should explain what the "size" means and whether it has a unit.
  - The log messages must reflect what is actually happening. For example, in the statements `log('Data is moved to the back of queue'); move_to_back(data);`, the log message is inaccurate the actual movement happens after this message. A better message is `log('Moving data to the back of queue');`.
- [ ] Try **NOT** to make the interface too specific to one situation.
  - Note the difference between a "task" and a "situation". For example, most of the Linux tools focus on **one task** but their interfaces are flexible enough to handle **many situations**.
  - A counter-example is: When I designed the `AddColumn` database migration class, I made the interface to take in arguments like `data_type`, `nullable`, `default_value`,etc.. This forces the user to use the  class only when they need to define the column with the given arguments. In other words, the interface only fits a limited number of "situations". Later I refined the interface to take a much more broader `column_definition` which the user can give whatever he/she wants to define the column. Sure, the user has more responsibility to ensure its correctness, but this is a balance between "making the interface more flexible" and "making the interface harder to be misused".
- [ ] Add copyright information when needed.
- [ ] Add modelines in favor of `vim` when needed.
- [ ] Avoid changing the current working directory.

## Testing

- Unit tests:
  - [ ] The code is written in a way that is friendly to unit tests.
  - [ ] All the existing unit tests must pass.
  - [ ] Maximize the test coverage. If some code is not covered, give reasonable explanation.
- File copying/moving (refer to the [shutil documentation](https://docs.python.org/3/library/shutil.html)):
  - [ ] Test the following cases:
    - 1). Target path does not exist.
    - 2). Target is a file/directory.
    - 3). Permission.
    - 4). A file/directory of the same name already exists.
    - 5). The target path is the same as the source path (copying/moving the same file).

## Git

- Commit messages:
  - [ ] **Follow the 7 rules** as discussed [here](https://chris.beams.io/posts/git-commit/#seven-rules).
    - 1). Separate subject from body with a blank line
    - 2). Limit the subject line to **50** characters
    - 3). Capitalize the subject line
    - 4). Do not end the subject line with a period
    - 5). Use the imperative mood in the subject line
      - A properly formed Git commit subject line should always be able to complete the following sentence:
      - If applied, this commit will _your subject line here_
      - Remember: Use of the imperative is important only in the subject line. You can relax this restriction when you’re writing the body.
      - Examples:
        - Good: 'Refactor subsystem X for readability'
        - Bad: 'Fixed bug with Y'
    - 6). Wrap the body at **72** characters
    - 7). Use the body to explain what and why vs. how.
  - [ ] **Avoid one-liner message.** Include the referenced issue ID, SHAs of the related commits, etc to explain why the commit is made. See the rule #7 above.
  - [ ] **Put "Fix \<issue URL\>"** in the commit message if the commit can fix the issue.
  - Refer to the following example:

```text
Describe briefly the topic in 50 characters

Elaborate the what major changes are done and why they are needed.
Wrap every line at 72 characters unless a URL must be used.

The elaboration can go in several paragraphs as long as needed. Follow
markdown syntax so the web interface can possibly display the content
nicely.

This commit also includes:

  - Use the "This commit also includes" list to mention the other minor
    things that are good to know.
  - Indent the list items with two blank spaces. Still wrap at the 72nd
    character and align the new line to the first letter.

Related issues & commits:

  - [1] organization/repo#123 (additional notes if needed)
  - [2] organization/repo@commit-sha-code (additional notes if needed)

This commit fixes:

  - Fix organization/repo#123
  - Fix organization/repo#456

```

- Commit history maintenance:
  - [ ] Use `rebase` to squash the commit history.
  - [ ] Do not rebase the work done by others without talking to them.
- Branches:
  - [ ] Prefix the branch name with my short name `ywen`.
- Pull Request:
  - [ ] Delete the remote branch after merge.
  - [ ] Use `git push origin BRANCH-NAME` to push a local branch to the remote. Use `-f` to force a PR update. **NOTE**: `BRANCH-NAME` should **NEVER** be a shared branch like `master`.
- Patches:
  - [ ] Use `git format-patch @{u}..` to create a series of patches.
  - [ ] Use `git am --directory=<dir> <path-to-patch>` to apply the patch.
- Misc.
  - [ ] Use `git diff` or `git diff --cached` to read through the diff content as a quick self-review.

## C++

Refer to [C++ Core Guidelines](http://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines).

### Classes

- [ ] Use `m_variable` naming convention.
- [ ] Class accessor modifiers, `private`, `protected`, and `public`, should appear only once.
- [ ] Destructors should never throw. Implement another method to do the cleanup and let it throw. In the destructor, call this method and catch the exceptions.

### Error Handling

- [ ] Catch exceptions as mutable objects, not `const reference`. (Although the _C++ Core Guidelines_ think the constant reference is better, it is currently agreed to use non-const reference in my organization.)
- [ ] Do not catch all exceptions (`std::exception`). Only catch the necessary ones which can usually be seen from the context.

### Templates

- [ ] Templates should vary on types, not (mainly) on value of numbers.

### Miscellaneous

- [ ] Use `clang-format`.
- [ ] Update the copyright information in the source files.
- [ ] Arrange `#include` in the order of: project header files, followed by third-party header files, followed by standard header files.
- [ ] Use the syntax `namespace A::B::C ...` to define nested namespaces.
- [ ] Comment out the unused parameters to avoid unreferenced parameter warnings.

## Python

- [ ] `PEP8 (v1.4.6)` check must pass.
- [ ] Write Python 2 & 3 compatibile code.
  - Use all the possible `__future__` features including `absolute_import`, `division`, `print_function`, and `unicode_literals`.
- String manipulation:
  - [ ] Use `six.moves.shlex_quote` to quote strings.

## JavaScript

- Code style:
  - [ ] `npm run lint` passes.
  - [ ] `standard (v11.0.1)` passes.
- Common pitfalls:
  - [ ] Shallow-cloning vs. deep-cloning: Double check which one is desired.

## Shell

- [ ] Write POSIX-compliant shell scripts.
  - See [here](http://sites.harvard.edu/~lib113/reference/unix/portable_scripting.html) for a solution.
  - Use [`shellcheck`](https://www.shellcheck.net/) to check bash-ism. If needed, use the online tool which should be the latest version to check the script.
- [ ] Add **error handling** to the exit code of a command.
- [ ] Check command line syntax at the top and error out with a usage message (e.g., `test $# -eq 2 || ...`).
- [ ] Examine the quotation of the variables.
- [ ] In a `rm -rf` operation, if a variable is the first part of the path, such as `$FOO/bar`, one must be cautious that `$FOO` could be empty which results in the removal of `/bar`. If `/bar` happens to be a system folder, that will be disastrous. Use `${FOO:?not set}/bar` to prevent from deleting it accidentally.

## Misc

- [ ] All the `TODO(ywen)` and `FIXME(ywen)` items have been resolved.
  - Remember to check **ALL** the files: sometimes a `TODO` may be added to a file without an extension (such as `SConscript`).
- [ ] **Security**: The code is not vulnerable to security attacks.
- [ ] **Quote**: In some situations, the strings must be escaped correctly:
  - [ ] When assigning a string to a environmental variable, quotation is necessary.
  - [ ] Use consistent variable names.
- [ ] Think in URLs, not IP + port.
- [ ] Date & time:
  - Try to use ISO 8601 format, which is specified by `date -I`.
  - Always consider timezone.
- [ ] `chown`: Consider both user and group.
- [ ] Use Ansible playbooks for machine deployment.
  - Playbooks are supposed to be idempotent so if they are written correctly, you can fix your installation by iteratively refining the playbooks. The **point** is: try to avoid manual work because it's hardly repeatable.
- [ ] **Pull Request title**: Describe the user-visible behavior that you are fixing instead of what you changed to fix it.
