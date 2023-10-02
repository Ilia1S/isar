#!/usr/bin/env python3

import inspect
import time
import yaml

import redis

from avocado import Test

with open('server_data.yaml', 'r') as yaml_file:
    yaml_data = yaml.safe_load(yaml_file)
    redis_server = yaml_data['redis_server']
    redis_port = yaml_data['redis_port']

r = redis.Redis(
    host=redis_server,
    port=redis_port,
    db=0,
    decode_responses=True
)

p = r.pubsub()
p.subscribe('test_dev_arm32_av', 'test_dev_arm64_av', 'test_dev_rebuild_av')


class Seeds(Test):
    def check_status(self, status, e):
        if status == 'CANCEL':
            self.cancel(e)
        elif status == 'FAILURE':
            self.fail(e)
        elif status == 'SUCCESS':
            pass

    def publish_relevance(self, is_relevant):
        channel = inspect.currentframe().f_back.f_code.co_name
        if is_relevant == 'yes':
            r.publish(channel, 'yes')

    def publish_deps(self, status):
        channel = inspect.currentframe().f_back.f_code.co_name
        if status == 'SUCCESS':
            r.publish(channel, 'pass')
        elif status == 'FAILURE':
            r.publish(channel, 'fail')

    def perform_run(self, channel, celery_task):
        tests_are_binded = self.params.get('binded', default=False)
        if tests_are_binded:
            duration = 10
            continued = False
            end_time = time.time() + duration
            while time.time() < end_time:
                is_relevant = p.get_message()
                if is_relevant and is_relevant['channel'] == channel:
                    if is_relevant['data'] == 'yes':
                        continued = True
                        break
        if tests_are_binded and continued or not tests_are_binded:
            e = None
            while True:
                dep = p.get_message()
                if dep and dep['channel'] == channel:
                    if dep['data'] == 'pass':
                        try:
                            result = celery_task.delay()
                            result.get()
                            return 'SUCCESS', e
                        except Exception as exc:
                            e = str(exc)
                            return 'FAILURE', e
                    elif dep['data'] == 'fail':
                        caller = inspect.currentframe().f_back.f_code.co_name
                        e = f'{caller} will not be run due to {channel} failed'
                        return 'CANCEL', e
                time.sleep(1)
        elif tests_are_binded and not continued:
            caller = inspect.currentframe().f_back.f_code.co_name
            e = f'{caller} will be cancelled due to {channel} is not run'
            return 'CANCEL', e
