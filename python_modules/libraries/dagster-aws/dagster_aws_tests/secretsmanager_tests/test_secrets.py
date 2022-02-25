from dagster import ModeDefinition, execute_solid, solid
from dagster.core.execution.context.init import build_init_resource_context
from dagster_aws.ecr import fake_ecr_public_resource

from dagster_aws.secretsmanager import get_secrets_from_arns, secretsmanager_secrets_resource
from dagster_aws.secretsmanager.secrets import get_tagged_secrets
from dagster import check
from dagster.core.test_utils import create_run_for_test, environ, instance_for_test
import os
import json


def test_get_secrets_from_arns(mock_secretsmanager_resource):
    foo_secret = mock_secretsmanager_resource.create_secret(
        Name="foo_secret", SecretString="foo_value"
    )
    bar_secret = mock_secretsmanager_resource.create_secret(
        Name="bar_secret", SecretString="bar_value"
    )
    assert get_secrets_from_arns(
        mock_secretsmanager_resource, [foo_secret["ARN"], bar_secret["ARN"]]
    ) == {"foo_secret": foo_secret["ARN"], "bar_secret": bar_secret["ARN"]}

    baz_secret = mock_secretsmanager_resource.create_secret(
        Name="baz_secret", SecretString="baz_value"
    )
    assert get_secrets_from_arns(
        mock_secretsmanager_resource, [foo_secret["ARN"], bar_secret["ARN"], baz_secret["ARN"]]
    ) == {
        "foo_secret": foo_secret["ARN"],
        "bar_secret": bar_secret["ARN"],
        "baz_secret": baz_secret["ARN"],
    }


def test_get_tagged_secrets(mock_secretsmanager_resource):
    assert get_tagged_secrets(mock_secretsmanager_resource, "dagster") == {}

    foo_secret = mock_secretsmanager_resource.create_secret(
        Name="foo_secret", SecretString="foo_value", Tags=[{"Key": "dagster", "Value": "foo"}]
    )
    assert get_tagged_secrets(mock_secretsmanager_resource, "dagster") == {
        "foo_secret": foo_secret["ARN"]
    }

    mock_secretsmanager_resource.create_secret(
        Name="bar_secret", SecretString="bar_value", Tags=[{"Key": "airflow", "Value": "bar"}]
    )
    assert get_tagged_secrets(mock_secretsmanager_resource, "dagster") == {
        "foo_secret": foo_secret["ARN"]
    }

    baz_secret = mock_secretsmanager_resource.create_secret(
        Name="baz_secret", SecretString="baz_value", Tags=[{"Key": "dagster", "Value": "baz"}]
    )
    assert get_tagged_secrets(mock_secretsmanager_resource, "dagster") == {
        "foo_secret": foo_secret["ARN"],
        "baz_secret": baz_secret["ARN"],
    }


def test_secretmanager_secrets_resource(mock_secretsmanager_resource):
    foo_secret = mock_secretsmanager_resource.create_secret(
        Name="foo_secret", SecretString="foo_value", Tags=[{"Key": "dagster", "Value": "foo"}]
    )
    bar_secret = mock_secretsmanager_resource.create_secret(
        Name="bar_secret", SecretString="bar_value", Tags=[{"Key": "airflow", "Value": "bar"}]
    )
    _baz_secret = mock_secretsmanager_resource.create_secret(
        Name="baz_secret", SecretString="baz_value", Tags=[{"Key": "dagster", "Value": "baz"}]
    )
    asdf_secret = mock_secretsmanager_resource.create_secret(
        Name="asdf_secret", SecretString="asdf_value"
    )

    with secretsmanager_secrets_resource(
        build_init_resource_context(config={"secrets": [foo_secret["ARN"]]})
    ) as secret_map:
        assert secret_map == {"foo_secret": "foo_value"}

    with secretsmanager_secrets_resource(
        build_init_resource_context(config={"secrets": [foo_secret["ARN"], bar_secret["ARN"]]})
    ) as secret_map:
        assert secret_map == {"foo_secret": "foo_value", "bar_secret": "bar_value"}

    with secretsmanager_secrets_resource(
        build_init_resource_context(config={"secrets_tag": "dagster"})
    ) as secret_map:
        assert secret_map == {"foo_secret": "foo_value", "baz_secret": "baz_value"}

    with secretsmanager_secrets_resource(
        build_init_resource_context(
            config={"secrets_tag": "dagster", "secrets": [asdf_secret["ARN"]]}
        )
    ) as secret_map:
        assert secret_map == {
            "foo_secret": "foo_value",
            "baz_secret": "baz_value",
            "asdf_secret": "asdf_value",
        }

        assert os.getenv("foo_secret") is None
        assert os.getenv("baz_secret") is None
        assert os.getenv("asdf_secret") is None

    with secretsmanager_secrets_resource(
        build_init_resource_context(
            config={
                "secrets_tag": "dagster",
                "secrets": [asdf_secret["ARN"]],
                "add_to_environment": True,
            }
        )
    ) as secret_map:
        assert secret_map == {
            "foo_secret": "foo_value",
            "baz_secret": "baz_value",
            "asdf_secret": "asdf_value",
        }

        assert os.getenv("foo_secret") == "foo_value"
        assert os.getenv("baz_secret") == "baz_value"
        assert os.getenv("asdf_secret") == "asdf_value"
