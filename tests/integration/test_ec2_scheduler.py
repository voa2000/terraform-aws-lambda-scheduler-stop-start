"""Tests for the ec2 scheduler."""

import boto3

from package.scheduler.ec2_handler import Ec2Scheduler

from .fixture import launch_ec2_instances

import pytest


@pytest.mark.parametrize(
    "aws_region, tag_key, tag_value, result_count",
    [
        (
            "eu-west-1",
            "tostop-ec2-test-1",
            "true",
            {"Code": 80, "Name": "stopped"},
        ),
        (
            "eu-west-1",
            "badtagkey",
            "badtagvalue",
            {"Code": 16, "Name": "running"},
        ),
    ],
)
def test_stop_ec2_scheduler(aws_region, tag_key, tag_value, result_count):
    """Verify stop ec2 scheduler class method."""
    client = boto3.client("ec2", region_name=aws_region)
    instances = launch_ec2_instances(2, aws_region, tag_key, tag_value)
    instance_ids = [x["InstanceId"] for x in instances["Instances"]]

    try:
        client.get_waiter("instance_running").wait(InstanceIds=instance_ids)
        ec2_scheduler = Ec2Scheduler(aws_region)
        ec2_scheduler.stop("tostop-ec2-test-1", "true")
        if tag_key == "tostop-ec2-test-1" and tag_value == "true":
            client.get_waiter("instance_stopped").wait(
                InstanceIds=instance_ids
            )

        ec2_describe = client.describe_instances(InstanceIds=instance_ids)
        for ec2 in ec2_describe["Reservations"][0]["Instances"]:
            assert ec2["State"] == result_count
    finally:
        # Clean aws account
        client.terminate_instances(InstanceIds=instance_ids)


@pytest.mark.parametrize(
    "aws_region, tag_key, tag_value, result_count",
    [
        (
            "eu-west-1",
            "tostop-ec2-test-2",
            "true",
            {"Code": 16, "Name": "running"},
        ),
        (
            "eu-west-1",
            "badtagkey",
            "badtagvalue",
            {"Code": 80, "Name": "stopped"},
        ),
    ],
)
def test_start_ec2_scheduler(aws_region, tag_key, tag_value, result_count):
    """Verify start ec2 scheduler class method."""
    client = boto3.client("ec2", region_name=aws_region)
    instances = launch_ec2_instances(2, aws_region, tag_key, tag_value)
    instance_ids = [x["InstanceId"] for x in instances["Instances"]]

    try:
        client.get_waiter("instance_running").wait(InstanceIds=instance_ids)
        client.stop_instances(InstanceIds=instance_ids)
        client.get_waiter("instance_stopped").wait(InstanceIds=instance_ids)
        ec2_scheduler = Ec2Scheduler(aws_region)
        ec2_scheduler.start("tostop-ec2-test-2", "true")
        if tag_key == "tostop-ec2-test-2" and tag_value == "true":
            client.get_waiter("instance_running").wait(
                InstanceIds=instance_ids
            )

        ec2_describe = client.describe_instances(InstanceIds=instance_ids)
        for ec2 in ec2_describe["Reservations"][0]["Instances"]:
            assert ec2["State"] == result_count
    finally:
        # Clean aws account
        client.terminate_instances(InstanceIds=instance_ids)
