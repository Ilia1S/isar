#!/usr/bin/env python3

from seeds import Seeds
from celery_tasks import *


class AvDevTest(Seeds):

    """
    Developer's test

    :avocado: tags=dev,fast,full
    """

    def test_dev_arm32_av(self):
        try:
            self.publish_relevance('yes')
            result = dev_arm32_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_dev_arm64_av(self):
        try:
            self.publish_relevance('yes')
            result = dev_arm64_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_dev_rebuild_av(self):
        try:
            self.publish_relevance('yes')
            result = dev_rebuild_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_dev_run_amd64_bullseye_av(self):
        status, e = self.perform_run(channel='test_dev_rebuild_av',
                                     celery_task=dev_run_amd64_bullseye_cel)
        self.check_status(status, e)

    def test_dev_run_arm64_bullseye_av(self):
        status, e = self.perform_run(channel='test_dev_arm64_av',
                                     celery_task=dev_run_arm64_bullseye_cel)
        self.check_status(status, e)

    def test_dev_run_arm_bullseye_av(self):
        status, e = self.perform_run(channel='test_dev_arm32_av',
                                     celery_task=dev_run_arm_bullseye_cel)
        self.check_status(status, e)
