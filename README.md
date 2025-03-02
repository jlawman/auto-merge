## Auto Merge

A simple tool to automatically merge or reject Pull requests from coding agents based on instructions they received. If the comment from the PR contains instructions that match the changes the PR will be merged, otherwise it will be rejected and the PR will be closed.

### Setup

1. Copy the files in the .github folder to your own repo.
2. Set an ANTHROPIC_API_KEY in the repo secrets.

### Examples

#### Rejected PR
![Example of a rejected PR](media/example-rejected.png)

#### Approved PR
![Example of an approved PR](media/example-approved.png)




