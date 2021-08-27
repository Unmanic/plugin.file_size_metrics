#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    plugins.history.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     25 Aug 2021, (8:51 PM)

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
from operator import attrgetter

from file_size_metrics.lib.database import Database, HistoricTasks, HistoricTaskProbe


class Data(object):

    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger
        self.db = Database(settings, logger)
        self.create_db_connection()

    @staticmethod
    def close():
        Database.close()

    def create_db_connection(self):
        # First migrate old data if required
        self.db.migrate_data()
        # Create database schema
        self.db.create_db_schema()

    def get_total_historic_task_list_count(self):
        query = HistoricTasks.select().order_by(HistoricTasks.id.desc())
        return query.count()

    def get_historic_task_list_filtered_and_sorted(self, order=None, start=0, length=None, search_value=None,
                                                   id_list=None,
                                                   task_success=None):
        try:
            query = (HistoricTasks.select())

            if id_list:
                query = query.where(HistoricTasks.id.in_(id_list))

            if search_value:
                query = query.where(HistoricTasks.task_label.contains(search_value))

            if task_success:
                query = query.where(HistoricTasks.task_success.in_([task_success]))

            # Get order by
            if order:
                if order.get("dir") == "asc":
                    order_by = attrgetter(order.get("column"))(HistoricTasks).asc()
                else:
                    order_by = attrgetter(order.get("column"))(HistoricTasks).desc()

                if length:
                    query = query.order_by(order_by).limit(length).offset(start)

        except HistoricTasks.DoesNotExist:
            # No historic entries exist yet
            self.logger.warning("No historic tasks exist yet.")
            query = []

        return query.dicts()

    def get_history_probe_data(self, task_id):
        query = HistoricTaskProbe.select().where(HistoricTaskProbe.historictask_id.in_(task_id))

        # Iterate over historical tasks and append them to the task data
        results = []
        for task in query:
            # Set params as required in template
            item = {
                'type':     task.type,
                'abspath':  task.abspath,
                'basename': task.basename,
                'size':     task.size,
            }
            results.append(item)

        return results

    def calculate_total_file_size_difference(self):
        # TODO: Only show results for successful records
        results = {}
        from peewee import fn
        source_query = HistoricTaskProbe.select(
            fn.SUM(HistoricTaskProbe.size).alias('total')
        ).where(HistoricTaskProbe.type == 'source')
        destination_query = HistoricTaskProbe.select(
            fn.SUM(HistoricTaskProbe.size).alias('total')
        ).where(HistoricTaskProbe.type == 'destination')

        for r in source_query:
            results['source'] = r.total
        for r in destination_query:
            results['destination'] = r.total

        return results

    def prepare_filtered_historic_tasks(self, request_dict):
        # Generate filters for query
        draw = request_dict.get('draw')
        start = request_dict.get('start')
        length = request_dict.get('length')

        search = request_dict.get('search')
        search_value = search.get("value")

        # Get sort order
        filter_order = request_dict.get('order')[0]
        order_direction = filter_order.get('dir', 'desc')
        columns = request_dict.get('columns')
        order_column_name = columns[filter_order.get('column')].get('name', 'finish_time')
        order = {
            "column": order_column_name,
            "dir":    order_direction,
        }

        # Get total count
        records_total_count = self.get_total_historic_task_list_count()

        # Get quantity after filters (without pagination)
        records_filtered_count = self.get_historic_task_list_filtered_and_sorted(order=order, start=0, length=0,
                                                                                 search_value=search_value).count()

        # Get filtered/sorted results
        task_results = self.get_historic_task_list_filtered_and_sorted(order=order, start=start, length=length,
                                                                       search_value=search_value)

        # Build return data
        return_data = {
            "draw":            draw,
            "recordsTotal":    records_total_count,
            "recordsFiltered": records_filtered_count,
            "successCount":    0,
            "failedCount":     0,
            "data":            []
        }

        # Iterate over historical tasks and append them to the task data
        for task in task_results:
            start_time = ''
            if task.get('start_time'):
                start_time = task.get('start_time').isoformat()
            finish_time = ''
            if task.get('finish_time'):
                finish_time = task.get('finish_time').isoformat()
            # Set params as required in template
            item = {
                'id':           task.get('id'),
                'selected':     False,
                'task_label':   task.get('task_label'),
                'task_success': task.get('task_success'),
                'start_time':   start_time,
                'finish_time':  finish_time,
            }
            # Increment counters
            if item['task_success']:
                return_data["successCount"] += 1
            else:
                return_data["failedCount"] += 1
            return_data["data"].append(item)

        # Return results
        return return_data
