"""
Helper functions for working with S3 and STS
"""
from typing import List, Optional, Tuple, Union

from . import models, schemas, settings


def sanitize(name: str):
    # TODO
    return name


def getWorkspaceKey(workspace: models.Workspace):
    """
    Determine object path for a given workspace
    """
    root = "public" if workspace.public else "private"
    return f"{root}/{workspace.owner.username}/{sanitize(workspace.name)}"


def makeRoleSessionName(user: schemas.UserDB, workspace: Optional[models.Workspace]):
    return f"{user.id}::{workspace}"


def makePolicy(
    user: schemas.UserDB,
    bucket: str,
    policies: List[Tuple[Union[models.Workspace, None], schemas.ShareType]],
):
    """
    Make a policy for the given user to access s3 based on
    https://aws.amazon.com/premiumsupport/knowledge-center/s3-folder-user-access/
    """
    resourceBase = f"arn:aws:s3:::{bucket}"
    statements: List[dict] = []
    added_defaults = False
    for workspace, sharetype in policies:
        if workspace is None and not added_defaults:
            # only add these policies once
            added_defaults = True
            # This is a blanket user policy
            statements.append(
                {
                    "Action": ["s3:ListAllMyBuckets", "s3:GetBucketLocation"],
                    "Effect": "Allow",
                    "Resource": ["arn:aws:s3:::*"],
                }
            )
            # General public access
            statements.append(
                {
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [resourceBase],
                    "Condition": {
                        "StringLike": {"s3:prefix": "public", "s3:delimiter": "/"}
                    },
                }
            )
            statements.append(
                {
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [resourceBase],
                    "Condition": {"StringLike": {"s3:prefix": "public/*"}},
                }
            )
            statements.append(
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"{resourceBase}/public/*"],
                }
            )
            # Private user access
            statements.append(
                {
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [resourceBase],
                    "Condition": {
                        "StringLike": {
                            "s3:prefix": f"private/{user.username}",
                            "s3:delimiter": "/",
                        }
                    },
                }
            )
            statements.append(
                {
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [resourceBase],
                    "Condition": {
                        "StringLike": {"s3:prefix": f"private/{user.username}/*"}
                    },
                }
            )
            statements.append(
                {
                    "Effect": "Allow",
                    "Action": ["s3:*"],
                    "Resource": [f"{resourceBase}/private/{user.username}/*"],
                }
            )
        elif workspace is not None:
            # This is a specific workspace share policy
            # General public access
            workspacekey = getWorkspaceKey(workspace)
            statements.append(
                {
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [resourceBase],
                    "Condition": {
                        "StringLike": {"s3:prefix": workspacekey, "s3:delimiter": "/"}
                    },
                }
            )
            statements.append(
                {
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [resourceBase],
                    "Condition": {"StringLike": {"s3:prefix": f"{workspacekey}/*"}},
                }
            )
            statements.append(
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"{resourceBase}/{workspacekey}/*"],
                }
            )
            if (
                sharetype is schemas.ShareType.READWRITE
                or sharetype is schemas.ShareType.OWN
            ):
                statements.append(
                    {
                        "Effect": "Allow",
                        "Action": ["s3:PutObject", "s3:DeleteObject"],
                        "Resource": [f"{resourceBase}/{workspacekey}/*"],
                    }
                )

    return {
        "Version": "2012-10-17",
        "Statement": statements,
    }


def makeEmptyPolicy():
    return {
        "Version": "2012-10-17",
        "Statement": [],
    }
