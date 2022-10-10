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

# Third party imports
# from abc import update_abstractmethods
from cloudify import ctx

# Local imports
from openstack_sdk.resources.networks import OpenstackSecurityGroupRule
from openstack_sdk.resources.networks import OpenstackSecurityGroup
from openstack_plugin.decorators import with_openstack_resource
from openstack_plugin.constants import (RESOURCE_ID,
                                        SECURITY_GROUP_RULE_OPENSTACK_TYPE)
from openstack_plugin.utils import (validate_resource_quota,
                                    add_resource_list_to_runtime_properties,
                                    drift_state)


@with_openstack_resource(OpenstackSecurityGroupRule)
def create(openstack_resource):
    """
    Create openstack security group rule instance
    :param openstack_resource: instance of openstack security group rule
    resource
    """
    created_resource = openstack_resource.create()
    ctx.instance.runtime_properties[RESOURCE_ID] = created_resource.id


@with_openstack_resource(OpenstackSecurityGroupRule)
def poststart(openstack_resource):
    """
    Get qurrent status of openstack network for check_drift
    :param openstack_resource: instance of openstack network resource
    """
    ctx.logger.debug("Set expected configuration")
    ctx.instance.runtime_properties['expected_configuration'] = \
        openstack_resource.get()


@with_openstack_resource(OpenstackSecurityGroupRule)
def delete(openstack_resource):
    """
    Delete current openstack security group rule instance
    :param openstack_resource: instance of openstack security group rule
    resource
    """
    openstack_resource.delete()


@with_openstack_resource(OpenstackSecurityGroupRule)
def check_drift(openstack_resource):
    """
    This method is to check drift of configuration
    :param openstack_resource: Instance of current openstack network
    """
    return drift_state(ctx.logger, openstack_resource)


@with_openstack_resource(OpenstackSecurityGroupRule)
def list_security_group_rules(openstack_resource, query=None):
    """
    List openstack security group rules based on filters applied
    :param openstack_resource: Instance of current openstack security group
    rule
    :param kwargs query: Optional query parameters to be sent to limit
    the security group rules being returned.
    """

    security_group_rules = openstack_resource.list(query)
    add_resource_list_to_runtime_properties(SECURITY_GROUP_RULE_OPENSTACK_TYPE,
                                            security_group_rules)


@with_openstack_resource(OpenstackSecurityGroupRule)
def creation_validation(openstack_resource):
    """
    This method is to check if we can create security group rule resource
    in openstack
    :param openstack_resource: Instance of current openstack security rule
    group
    """
    validate_resource_quota(openstack_resource,
                            SECURITY_GROUP_RULE_OPENSTACK_TYPE)
    ctx.logger.debug('OK: security group rule configuration is valid')


@with_openstack_resource(OpenstackSecurityGroupRule)
def establish(openstack_resource):
    _update_secgroup_expected_configuration(ctx)


@with_openstack_resource(OpenstackSecurityGroupRule)
def unlink(openstack_resource):
    _update_secgroup_expected_configuration(ctx)


def _update_secgroup_expected_configuration(ctx):
    ctx.logger.debug(
        "Updating expected_configuration for {}".format(ctx.target.instance.id)
        )
    secgroup_id = ctx.target.instance.runtime_properties.get('id')
    client_config = ctx.target.node.properties.get('client_config')
    security_group = \
        OpenstackSecurityGroup(client_config=client_config,
                               logger=ctx.logger)
    result = security_group.find_security_group(secgroup_id)
    ctx.target.instance.runtime_properties['expected_configuration'] = \
        result
