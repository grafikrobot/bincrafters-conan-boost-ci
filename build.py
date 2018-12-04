#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan.packager import ConanMultiPackager
import os
import re
import platform


def get_value_from_recipe(search_string):
    with open("conanfile.py", "r") as conanfile:
        contents = conanfile.read()
        result = re.search(search_string, contents)
    return result


def get_name_from_recipe():
    return get_value_from_recipe(r'''name\s*=\s*["'](\S*)["']''').groups()[0]


def get_version_from_recipe():
    return get_value_from_recipe(r'''version\s*=\s*["'](\S*)["']''').groups()[0]


def get_default_vars():
    username = os.getenv("CONAN_USERNAME", "bincrafters")
    channel = os.getenv("CONAN_CHANNEL", "testing")
    version = get_version_from_recipe()
    build = "gcc_7"
    return username, channel, version, build.upper()


def is_ci_running():
    return os.getenv("APPVEYOR_REPO_NAME", "") or os.getenv("TRAVIS_REPO_SLUG", "")


def get_ci_vars():
    reponame_a = os.getenv("APPVEYOR_REPO_NAME")
    repobranch_a = os.getenv("APPVEYOR_REPO_BRANCH")

    reponame_t = os.getenv("TRAVIS_REPO_SLUG")
    repobranch_t = os.getenv("TRAVIS_BRANCH")

    username = reponame_a.split("/")[0] if reponame_a else reponame_t.split("/")[0]
    channel, version, build = repobranch_a.split("/") if repobranch_a else repobranch_t.split("/")
    return username, channel, version, build.upper()


def get_env_vars():
    return get_ci_vars() if is_ci_running() else get_default_vars()


def get_os():
    return platform.system().replace("Darwin", "Macos")


if __name__ == "__main__":
    name = get_name_from_recipe()
    username, channel, version, build = get_env_vars()
    reference = "{0}/{1}".format(name, version)
    upload = "https://api.bintray.com/conan/{0}/public-conan".format(username)
    upload_only_when_stable = True
    stable_branch_pattern = os.getenv("CONAN_STABLE_BRANCH_PATTERN", 'stable/*')
    if os.getenv('CONAN_UPLOAD_ONLY_WHEN_STABLE', '1') != '1':
        upload_only_when_stable = False
        stable_branch_pattern = None
        del os.environ['CONAN_UPLOAD_ONLY_WHEN_STABLE']
        if 'CONAN_STABLE_BRANCH_PATTERN' in os.environ:
            del os.environ['CONAN_STABLE_BRANCH_PATTERN']

    build = os.getenv("BUILD", build)
    if build:
        build_env = os.getenv(build, None)
        if build_env:
            for env_var in build_env.split():
                name, value = env_var.split("=", 1)
                os.environ[name] = value
                print("%s=%s" % (name, os.getenv(name)))

    builder = ConanMultiPackager(
        username=os.getenv("CONAN_USERNAME", username),
        channel=os.getenv("CONAN_CHANNEL", channel),
        reference=os.getenv("CONAN_REFERENCE", reference),
        upload=os.getenv("CONAN_UPLOAD", upload),
        remotes=if os.getenv("CONAN_REMOTES") upload+","+os.getenv("CONAN_REMOTES") else upload,
        upload_only_when_stable=upload_only_when_stable,
        stable_branch_pattern=stable_branch_pattern)

    builder.add_common_builds(
        shared_option_name=os.getenv('CONAN_SHARED_OPTION_NAME', name + ":shared"))
    builder.run()
