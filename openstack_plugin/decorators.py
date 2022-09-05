# #######
# Copyright (c) 2019 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Standard Imports
import sys

# Third party imports
from openstack import exceptions
from cloudify import ctx as CloudifyContext
from cloudify.exceptions import NonRecoverableError
from cloudify.utils import exception_to_error_cause
from cloudify.decorators import operation

# Local imports
from openstack_plugin.compat import Compat
from openstack_sdk.common import (InvalidDomainException,
                                  QuotaException,
                                  InvalidINSecureValue)
from openstack_plugin.utils import (
    resolve_ctx,
    get_current_operation,
    prepare_resource_instance,
    use_external_resource,
    update_runtime_properties_for_operation_task,
    update_runtime_properties_for_node_v2,
    is_compat_node,
    set_external_resource
)
# Local imports
from openstack_plugin.constants import (
    CLOUDIFY_STOP_OPERATION,
    CLOUDIFY_DELETE_OPERATION,
    CLOUDIFY_UNLINK_OPERATION,
    CLOUDIFY_UPDATE_OPERATION,
    CLOUDIFY_UPDATE_PROJECT_OPERATION,
    RESOURCE_ID
)
EXCEPTIONS = (exceptions.SDKException,
              InvalidDomainException,
              QuotaException,
              InvalidINSecureValue)


def with_openstack_resource(class_decl,
                            existing_resource_handler=None,
                            **existing_resource_kwargs):
    """
    :param class_decl: This is a class for the openstack resource need to be
    invoked
    :param existing_resource_handler: This is a method that handle any
    custom operation need to be done in case "use_external_resource" is set
    to true
    :param existing_resource_kwargs: This is an extra param that we may need
    to pass to the external resource  handler
    :return: a wrapper object encapsulating the invoked function
    """
    def wrapper_outer(func):
        def wrapper_inner(**kwargs):
            # Get the context for the current task operation
            ctx = kwargs.pop('ctx', CloudifyContext)

            # Resolve the actual context which need to run operation,
            # the context could be belongs to relationship context or actual
            # node context
            ctx_node = resolve_ctx(ctx)

            # Get the current operation name
            operation_name = get_current_operation()
            try:
                # Prepare the openstack resource that need to execute the
                # current task operation
                # Make sure we cleaned up resource
                # before performing create in heal.
                if 'heal' in ctx.workflow_id and 'create' in operation_name:
                    update_runtime_properties_for_operation_task(
                        CLOUDIFY_DELETE_OPERATION,
                        ctx_node)
                resource = \
                    prepare_resource_instance(class_decl, ctx_node, kwargs)

                if use_external_resource(ctx_node, resource,
                                         existing_resource_handler,
                                         **existing_resource_kwargs):
                    return
                # check resource_id before stop/delete for already cleaned up
                if operation_name in (
                    CLOUDIFY_STOP_OPERATION, CLOUDIFY_DELETE_OPERATION,
                    CLOUDIFY_UNLINK_OPERATION
                ):
                    if not ctx_node.instance.runtime_properties.get(
                        RESOURCE_ID
                    ):
                        ctx.logger.info(
                            'Instance is already uninitialized.')
                        return
                # run action
                kwargs['openstack_resource'] = resource
                return func(**kwargs)
            except EXCEPTIONS as errors:
                _, _, tb = sys.exc_info()
                raise NonRecoverableError(
                    'Failure while trying to run operation:'
                    '{0}: {1}'.format(operation_name, errors.message),
                    causes=[exception_to_error_cause(errors, tb)])
            finally:
                update_runtime_properties_for_operation_task(operation_name,
                                                             ctx_node,
                                                             resource)
                # Update "external_resource" runtime property when running
                # any update operation or update project for external resource
                set_external_resource(ctx_node, resource, [
                    CLOUDIFY_UPDATE_PROJECT_OPERATION,
                    CLOUDIFY_UPDATE_OPERATION
                ])
        return wrapper_inner
    return wrapper_outer


def with_compat_node(func):
    """
    This decorator is used to transform nodes properties for openstack nodes
    with version 2.X to be compatible with new nodes support by version 3.x
    :param func: The decorated function
    :return: Wrapped function
    """
    def wrapper(**kwargs):
        ctx = kwargs.get('ctx', CloudifyContext)

        # Resolve the actual context which need to run operation,
        # the context could be belongs to relationship context or actual
        # node context
        ctx_node = resolve_ctx(ctx)
        # Check to see if we need to do properties transformation or not
        kwargs_config = {}
        if is_compat_node(ctx_node):
            compat = Compat(context=ctx_node, **kwargs)
            kwargs_config = compat.transform()

        if not kwargs_config:
            kwargs_config = kwargs
        try:
            return func(**kwargs_config)
        finally:
            update_runtime_properties_for_node_v2(ctx_node, kwargs_config)
    return operation(func=wrapper, resumable=True)


def with_multiple_data_sources(clean_duplicates_handler=None):
    def wrapper_outer(func):
        def wrapper_inner(config, **kwargs):
            # Check if the current node has "use_compact_node"
            if is_compat_node(CloudifyContext):
                kwargs['allow_multiple'] = True
            res = func(config, **kwargs)
            if kwargs.get('allow_multiple') and clean_duplicates_handler:
                clean_duplicates_handler(config)
            return res
        return wrapper_inner
    return wrapper_outer
