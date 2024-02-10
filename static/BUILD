load("@aspect_rules_rollup//rollup:defs.bzl", "rollup")
load("@aspect_rules_ts//ts:defs.bzl", "ts_project")

filegroup(
    name = "static",
    srcs = [
        ":app",
        ":bundle",
        ":styles",
        ":html",
    ],
    visibility = ["//visibility:public"],
)

ts_project(
    name = "app",
    srcs = glob(["**/*.ts"]),
    declaration = True,
    tsconfig = "//:tsconfig",
    deps = [
        "//:node_modules/tslib",
        "//:node_modules/rxjs"
    ],
)


rollup(
    name = "bundle",
    config_file = ":rollup.config.js",
    entry_point = ":index.js",
    node_modules = "//:node_modules",
    sourcemap = "false",
    deps = [
        ":app",
        "//:node_modules/@rollup/plugin-node-resolve"
    ],
)

filegroup(
    name = "styles",
    srcs = [
        "base.css",
    ],
)


filegroup(
    name = "html",
    srcs = [
        "index.html",
    ],
)
