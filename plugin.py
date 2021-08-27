#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     25 April 2021, (3:41 AM)

    Copyright:
        Copyright (C) 2021 Josh Sunnex

        This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
        Public License as published by the Free Software Foundation, version 3.

        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
        implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
        for more details.

        You should have received a copy of the GNU General Public License along with this program.
        If not, see <https://www.gnu.org/licenses/>.

"""
import json
import logging
import os

from unmanic.libs.unplugins.settings import PluginSettings

from file_size_metrics.lib.history import Data

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.file_size_metrics")


class Settings(PluginSettings):
    settings = {}


def get_historical_data(data):
    results = []
    arguments = data.get('arguments')
    request_body = arguments.get('data', [])
    if request_body:
        request_dict = json.loads(request_body[0])

        settings = Settings()
        data = Data(settings, logger)

        # Return a list of historical tasks based on the request JSON body
        results = data.prepare_filtered_historic_tasks(request_dict)

        data.close()

    return json.dumps(results, indent=2)


def get_historical_data_details(data):
    results = []
    arguments = data.get('arguments')
    task_id = arguments.get('task_id', [])
    if task_id:
        settings = Settings()
        data = Data(settings, logger)

        # Return a list of historical tasks based on the request JSON body
        results = data.get_history_probe_data(task_id)

        data.close()

    return json.dumps(results, indent=2)


def get_total_size_change_data_details(data):
    settings = Settings()
    data = Data(settings, logger)

    # Return a list of historical tasks based on the request JSON body
    results = data.calculate_total_file_size_difference()

    data.close()

    return json.dumps(results, indent=2)


def on_worker_process(data):
    """
    Runner function - enables additional configured processing jobs during the worker stages of a task.

    The 'data' object argument includes:
        exec_command            - A command that Unmanic should execute. Can be empty.
        command_progress_parser - A function that Unmanic can use to parse the STDOUT of the command to collect progress stats. Can be empty.
        file_in                 - The source file to be processed by the command.
        file_out                - The destination that the command should output (may be the same as the file_in if necessary).
        original_file_path      - The absolute path to the original file.
        repeat                  - Boolean, should this runner be executed again once completed with the same variables.

    :param data:
    :return:
    
    """
    return data


def render_frontend_panel(data):
    if data.get('path') in ['list', '/list', '/list/', '/list/']:
        data['content_type'] = 'application/json'
        data['content'] = get_historical_data(data)
        return

    if data.get('path') in ['conversionDetails', '/conversionDetails', '/conversionDetails/', '/conversionDetails/']:
        data['content_type'] = 'application/json'
        data['content'] = get_historical_data_details(data)
        return

    if data.get('path') in ['totalSizeChange', '/totalSizeChange', '/totalSizeChange/', '/totalSizeChange/']:
        data['content_type'] = 'application/json'
        data['content'] = get_total_size_change_data_details(data)
        return

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'index.html'))) as f:
        data['content'] = f.read()

    from pprint import pprint
    pprint(data)

    return data
