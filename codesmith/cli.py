#!/usr/bin/env python

# Copyright 2019 [name of copyright owner]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" test script for building from yaml format file """

import argparse
import logging
import os
import re
import sys

from digraphtools import digraphtools as dgt
import yaml


BUILD_FILE = "./artifacts.yaml"
ACTION_KEY = "shell"
DEPENDS_KEY = "depends-on"
FIRST_DEPENDENCY_KEY = "first-depends"


def debug(msg):
    logging.debug(msg)


def info(msg):
    logging.info(msg)


def fail(msg):
    logging.critical(msg)
    sys.exit(1)


def loadBuildFile(buildFile):
    with open(buildFile, "r") as stream:
        buildData = yaml.load(stream, Loader=yaml.FullLoader)

    depgraph = {}

    for target, data in buildData.items():
        if isinstance(data, str):
            action = data
            firstDependency = None
            dependencies = {}

            updateData = {
                ACTION_KEY: action,
                FIRST_DEPENDENCY_KEY: firstDependency,
                DEPENDS_KEY: dependencies,
            }

            buildData[target] = updateData
        else:
            deps = data.get(DEPENDS_KEY, {})
            dependencies = [deps] if isinstance(deps, str) else deps
            action = data.get(ACTION_KEY, None)
            firstDependency = dependencies[0] if dependencies else None

            updateData = {
                ACTION_KEY: action,
                FIRST_DEPENDENCY_KEY: firstDependency,
                DEPENDS_KEY: set(dependencies),
            }
            buildData[target].update(updateData)

        if target in depgraph:
            fail(f"ERROR: '{target}' repeated")

        depgraph[target] = updateData[DEPENDS_KEY]

    debug(buildData)
    return buildData, depgraph


def getTaskList(depgraph, targets):
    return [dgt.dfs_topsort_traversal(depgraph, t) for t in targets]


def multireplace(data, reps):
    pattern = re.compile(
        "|".join(re.escape(rep) for rep in sorted(reps.keys(), key=len, reverse=True))
    )

    return pattern.sub(lambda match: reps[match.group(0)], data)


def convertActionPatterns(target, data):
    action = data[ACTION_KEY]
    if action is None:
        return None

    primaryDep = data[FIRST_DEPENDENCY_KEY]
    tdir = os.path.dirname(target)
    tfile = os.path.basename(target)
    replacements = {
        "$(<)": primaryDep,
        "$<": primaryDep,
        "$(@D)": tdir,
        "$(@F)": tfile,
        "$(@)": target,
        "$@": target,
    }

    return multireplace(action, replacements)


def executeTarget(target, data, dryRun):
    debug(f"target = '{target}'")
    debug(data)
    convertedData = convertActionPatterns(target, data)
    debug(f"data = '{convertedData}'")
    if dryRun:
        if data.get(".PHONY"):
            info("Dry Run of .PHONY target")
        else:
            info("Dry Run of normal target; will eventually just touch!")
    else:
        print("Will eventually execute")


def processCmdline():
    loglevels = ["DEBUG", "INFO", "ERROR", "CRITICAL"]
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="*", help="ordered list of targets to run")
    parser.add_argument(
        "-C",
        "--directory",
        metavar="DIR",
        action="append",
        help="Change to directory DIR before doing anything.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="log_level",
        action="store_const",
        const="DEBUG",
        default="INFO",
        help="Print debugging information.",
    )
    parser.add_argument(
        "-f", "--file", default=BUILD_FILE, help="Read FILE as the build file."
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        "--recon",
        action="store_true",
        help="Touch targets instead of remaking.",
    )
    parser.add_argument(
        "-t", "--touch", action="store_true", help="Touch targets instead of remaking."
    )

    parser.add_argument(
        "--list-targets", action="store_true", help="List the available targets."
    )
    parser.add_argument("--log-file", help="specify file to write output to")
    parser.add_argument(
        "--log-level", default="INFO", choices=loglevels, help="set logging level"
    )
    args = parser.parse_args()

    loggingDict = {
        "format": "%(asctime)s %(levelname)s: %(message)s",
        "level": args.log_level,
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
    if args.log_file:
        loggingDict["filename"] = args.log_file
    logging.basicConfig(**loggingDict)

    if args.directory:
        for path in args.directory:
            debug(f"attempting to change to '{path}' directory")
            try:
                os.chdir(path)
            except os.FileNotFoundError:
                fail(f"Unable to change to '{path}'")
            info("Changed to '{path}' directory")

    debug("Completed parsing cmdline")
    debug(f"discovered args: '{args}'")
    return args


def runTargets(targets, buildData, dryRun):
    for target in targets:
        info(f"Current target: '{target}'")
        executeTarget(target, buildData[target], dryRun)


def main():
    args = processCmdline()
    buildData, depgraph = loadBuildFile(args.file)

    if args.list_targets:
        for target in buildData.keys():
            print(f"  {target}")
        sys.exit(0)

    taskList = getTaskList(depgraph, args.targets)
    for task in taskList:
        runTargets(task, buildData, args.dry_run)


if __name__ == "__main__":
    main()
