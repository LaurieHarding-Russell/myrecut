load("@npm//:defs.bzl", "npm_link_all_packages")
load("@aspect_rules_js//npm:defs.bzl", "npm_link_package")
load("@aspect_rules_ts//ts:defs.bzl", "ts_config")

load("@rules_python//python:defs.bzl", "py_binary", "py_test")
load("@rules_python//python:pip.bzl", "compile_pip_requirements")

npm_link_all_packages(name = "node_modules")

ts_config(
    name = "tsconfig",
    src = "tsconfig.json",
    visibility = ["//visibility:public"],
)

#Server stuff

# This rule adds a convenient way to update the requirements file.
compile_pip_requirements(
    name = "requirements",
    src = "requirements.in",
    requirements_txt = "requirements_lock.txt",
    requirements_windows = "requirements_windows.txt",
)

py_binary(
    name = "recut",
    srcs = ["recut.py", "RecutProcess.py", "RecutWord.py"],
    deps = [
        "@pypi//flask:pkg",
        "@pypi//waitress:pkg",
        "@pypi//deepspeech:pkg",
        "@pypi//moviepy:pkg",
        "@pypi//werkzeug:pkg",
        "@pypi//librosa:pkg"
    ],
    data = [
        "//static:static",
        "@pmml//file",
        "@scorer//file",
    ]
)
