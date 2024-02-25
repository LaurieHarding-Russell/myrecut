About:
A simple website for taking in a video and recutting it so that it plays the dialog you want.

Requirments:
- Bazelisk
- 

Run:
- `bazel run recut`
- go to `localhost:8080`

Typescript dev:
link node modules for your ide.
`ln -s bazel-bin/node_modules node_modules`

Add python dependency:
1. add to requirements.in
2. run `bazel run //:requirements.update`