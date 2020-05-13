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
import mock
import openstack.identity.v3.project
import openstack.identity.v2.user
import openstack.identity.v2.role
from cloudify.exceptions import NonRecoverableError

# Local imports
from openstack_sdk.resources.identity import OpenstackProject
from openstack_plugin.tests.base import OpenStackTestBase
from openstack_plugin.resources.identity import project
from openstack_plugin.constants import (RESOURCE_ID,
                                        IDENTITY_USERS,
                                        IDENTITY_GROUPS,
                                        IDENTITY_QUOTA,
                                        IDENTITY_ROLES,
                                        OPENSTACK_NAME_PROPERTY,
                                        OPENSTACK_TYPE_PROPERTY,
                                        PROJECT_OPENSTACK_TYPE)


@mock.patch('openstack.connect')
class ProjectTestCase(OpenStackTestBase):

    def setUp(self):
        super(ProjectTestCase, self).setUp()

    @property
    def resource_config(self):
        return {
            'name': 'test_project',
            'description': 'project_description'
        }

    @property
    def users(self):
        return [
            {
                'name': 'user-1',
                IDENTITY_ROLES: [
                    'test-role-1',
                    'test-role-2',
                    'test-role-3'
                ]
            }
        ]

    @property
    def groups(self):
        return [
            {
                'name': 'group-1',
                IDENTITY_ROLES: [
                    'test-role-1',
                    'test-role-2',
                    'test-role-3'
                ]
            }
        ]

    @property
    def node_properties(self):
        properties = super(ProjectTestCase, self).node_properties
        properties[IDENTITY_USERS] = self.users
        properties[IDENTITY_GROUPS] = self.groups
        return properties

    def test_create(self, mock_connection):
        # Prepare the context for create operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        project_instance = openstack.identity.v3.project.Project(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'test_project',
            'description': 'Testing Project',
            'domain_id': 'test_domain_id',
            'enabled': True,
            'is_domain': True,
            'links': ['test1', 'test2'],
            'parent_id': 'test_parent_id'

        })
        # Mock create project response
        mock_connection().identity.create_project = \
            mock.MagicMock(return_value=project_instance)

        # Call create project
        project.create(openstack_resource=None)

        self.assertEqual(self._ctx.instance.runtime_properties[RESOURCE_ID],
                         'a95b5509-c122-4c2f-823e-884bb559afe8')

        self.assertEqual(
            self._ctx.instance.runtime_properties[OPENSTACK_NAME_PROPERTY],
            'test_project')

        self.assertEqual(
            self._ctx.instance.runtime_properties[OPENSTACK_TYPE_PROPERTY],
            PROJECT_OPENSTACK_TYPE)

    def test_delete(self, mock_connection):
        # Prepare the context for delete operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')

        project_instance = openstack.identity.v3.project.Project(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'test_project',
            'description': 'Testing Project',
            'domain_id': 'test_domain_id',
            'enabled': True,
            'is_domain': True,
            'links': ['test1', 'test2'],
            'parent_id': 'test_parent_id'

        })
        # Mock get project response
        mock_connection().identity.get_project = \
            mock.MagicMock(return_value=project_instance)

        # Mock delete project response
        mock_connection().identity.delete_project = \
            mock.MagicMock(return_value=None)

        # Call delete project
        project.delete(openstack_resource=None)

        for attr in [RESOURCE_ID,
                     OPENSTACK_NAME_PROPERTY,
                     OPENSTACK_TYPE_PROPERTY]:
            self.assertNotIn(attr, self._ctx.instance.runtime_properties)

    def test_update(self, mock_connection):
        # Prepare the context for update operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.operations.update_project')

        old_project_instance = openstack.identity.v3.project.Project(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'test_project',
            'description': 'Testing Project',
            'domain_id': 'test_domain_id',
            'enabled': True,
            'is_domain': True,
            'links': ['test1', 'test2'],
            'parent_id': 'test_parent_id'

        })

        new_config = {
            'name': 'update_project',
        }

        new_project_instance = openstack.identity.v3.project.Project(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'test_updated_project',
            'description': 'Testing Project',
            'domain_id': 'test_domain_id',
            'enabled': True,
            'is_domain': True,
            'links': ['test1', 'test2'],
            'parent_id': 'test_parent_id'

        })

        # Mock get project response
        mock_connection().identity.get_project = \
            mock.MagicMock(return_value=old_project_instance)

        # Mock update project response
        mock_connection().identity.update_project = \
            mock.MagicMock(return_value=new_project_instance)

        # Call update project
        project.update(args=new_config, openstack_resource=None)

    def test_get_quota(self, mock_connection):
        # Prepare the context for get quota operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.operations.get_quota')

        quotas = {
              "cinder": {
                "snapshots_iscsi": -1,
                "gigabytes": 1000,
                "backup_gigabytes": 1000,
                "volumes_iscsi": -1,
                "snapshots": 100,
                "volumes": 50,
                "backups": 10,
                "gigabytes_iscsi": -1,
                "id": "af3a64f0e7b94a6ebb613d79706fa6ee"
              },
              "nova": {
                "injected_file_content_bytes": 10240,
                "metadata_items": 128,
                "server_group_members": 10,
                "server_groups": 10,
                "ram": 51200,
                "floating_ips": 10,
                "key_pairs": 100,
                "id": "af3a64f0e7b94a6ebb613d79706fa6ee",
                "instances": 10,
                "security_group_rules": 20,
                "injected_files": 50,
                "cores": 50,
                "fixed_ips": -1,
                "injected_file_path_bytes": 255,
                "security_groups": 10
              },
              "neutron": {
                "subnet": 10,
                "network": 10,
                "floatingip": 20,
                "security_group_rule": 100,
                "security_group": 10,
                "router": 10,
                "port": 50
              }
            }
        mock_connection().get_compute_quotas = \
            mock.MagicMock(return_value=quotas.get("nova"))
        mock_connection().get_network_quotas = \
            mock.MagicMock(return_value=quotas.get("neutron"))
        mock_connection().get_volume_quotas = \
            mock.MagicMock(return_value=quotas.get("cinder"))

        project.get_project_quota(openstack_resource=None)
        self.assertEqual(
            self._ctx.instance.runtime_properties['quota'], quotas)

    def test_update_project_quota(self, mock_connection):
        # Prepare the context for update quota operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.operations.update_quota')
        new_quota = {
            "quota": {
                "nova": {
                    "instances": 2
                }
            }
        }
        project.update_project_quota(openstack_resource=None, **new_quota)

    def test_list_projects(self, mock_connection):
        # Prepare the context for list projects operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.operations.list')

        projects = [
            openstack.identity.v3.project.Project(**{
                'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
                'name': 'test_project_1',
                'description': 'Testing Project 1',
                'domain_id': 'test_domain_id',
                'enabled': True,
                'is_domain': True,
                'links': ['test1', 'test2'],
                'parent_id': 'test_parent_id'
            }),
            openstack.identity.v3.project.Project(**{
                'id': 'a95b5509-c122-4c2f-823e-884bb559afe7',
                'name': 'test_project_2',
                'description': 'Testing Project 2',
                'domain_id': 'test_domain_id',
                'enabled': True,
                'is_domain': True,
                'links': ['test1', 'test2'],
                'parent_id': 'test_parent_id'
            }),
        ]

        # Mock list project response
        mock_connection().identity.projects = \
            mock.MagicMock(return_value=projects)

        # Mock find project response
        mock_connection().identity.find_project = \
            mock.MagicMock(return_value=self.project_resource)

        # Call list projects
        project.list_projects(openstack_resource=None)

        # Check if the projects list saved as runtime properties
        self.assertIn(
            'project_list',
            self._ctx.instance.runtime_properties)

        # Check the size of project list
        self.assertEqual(
            len(self._ctx.instance.runtime_properties['project_list']), 2)

    @mock.patch(
        'openstack_sdk.resources.identity.OpenstackProject.get_quota_sets')
    def test_creation_validation(self, mock_quota_sets, mock_connection):
        # Prepare the context for creation validation projects operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.validation.creation')

        projects = [
            openstack.identity.v3.project.Project(**{
                'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
                'name': 'test_project_1',
                'description': 'Testing Project 1',
                'domain_id': 'test_domain_id',
                'enabled': True,
                'is_domain': True,
                'links': ['test1', 'test2'],
                'parent_id': 'test_parent_id'
            }),
            openstack.identity.v3.project.Project(**{
                'id': 'a95b5509-c122-4c2f-823e-884bb559afe7',
                'name': 'test_project_2',
                'description': 'Testing Project 2',
                'domain_id': 'test_domain_id',
                'enabled': True,
                'is_domain': True,
                'links': ['test1', 'test2'],
                'parent_id': 'test_parent_id'
            }),
        ]

        # Mock list project response
        mock_connection().identity.projects = \
            mock.MagicMock(return_value=projects)

        # Mock the quota size response
        mock_quota_sets.return_value = 20

        # Call creation validation
        project.creation_validation(openstack_resource=None)

    @mock.patch(
        'openstack_plugin.resources.identity.project._assign_users')
    @mock.patch(
        'openstack_plugin.resources.identity.project._assign_groups')
    @mock.patch(
        'openstack_plugin.resources.identity.project._validate_users')
    @mock.patch(
        'openstack_plugin.resources.identity.project._validate_groups')
    def test_start(self, mock_validate_group, mock_validate_user,
                   mock_assign_group, mock_assign_user, mock_connection):
        # Prepare the context for start operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        project_instance = openstack.identity.v3.project.Project(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'test_project',
            'description': 'Testing Project',
            'domain_id': 'test_domain_id',
            'enabled': True,
            'is_domain': True,
            'links': ['test1', 'test2'],
            'parent_id': 'test_parent_id'

        })
        # Mock get project response
        mock_connection().identity.get_project = \
            mock.MagicMock(return_value=project_instance)

        # Call start project
        project.start(openstack_resource=None)
        mock_validate_user.assert_called()
        mock_validate_group.assert_called()
        mock_assign_user.assert_called()
        mock_assign_group.assert_called()

    @mock.patch(
        'openstack_plugin.resources.identity.project._assign_users')
    @mock.patch(
        'openstack_plugin.resources.identity.project._validate_users')
    def test_invalid_start(self, mock_validate, mock_assign, mock_connection):
        # Prepare the context for start operation
        properties = dict()
        properties[IDENTITY_QUOTA] = {'compute': 22}
        properties.update(self.node_properties)
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.start',
            test_properties=properties)

        project_instance = openstack.identity.v3.project.Project(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'test_project',
            'description': 'Testing Project',
            'domain_id': 'test_domain_id',
            'enabled': True,
            'is_domain': True,
            'links': ['test1', 'test2'],
            'parent_id': 'test_parent_id'

        })
        # Mock get project response
        mock_connection().identity.get_project = \
            mock.MagicMock(return_value=project_instance)

        with self.assertRaises(NonRecoverableError):
            # Call start project
            project.start(openstack_resource=None)
            mock_validate.assert_called()
            mock_assign.assert_called()

    def test_validate_users(self, mock_connection):
        # Prepare the context for start operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        user_instance_1 = openstack.identity.v2.user.User(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'user-1',
            'email': 'test_email',
            'is_enabled': True

        })
        role_instance_1 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe7',
            'name': 'test-role-1',
            'description': 'Testing Role 1',
            'is_enabled': True
        })
        role_instance_2 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe6',
            'name': 'test-role-2',
            'description': 'Testing Role 2',
            'domain_id': 'test_domain_id',
            'is_enabled': True
        })
        role_instance_3 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe5',
            'name': 'test-role-3',
            'description': 'Testing Role 3',
            'is_enabled': True
        })
        # Mock find user response
        mock_connection().identity.find_user = \
            mock.MagicMock(return_value=user_instance_1)

        # Mock find role response
        mock_connection().identity.find_role = \
            mock.MagicMock(side_effect=[role_instance_1,
                                        role_instance_2,
                                        role_instance_3])

        # Call start project
        project._validate_users(self.client_config, self.users)

    def test_assign_users(self, mock_connection):
        # Prepare the context for start operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        user_instance_1 = openstack.identity.v2.user.User(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'user-1',
            'email': 'test_email',
            'is_enabled': True

        })
        role_instance_1 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe7',
            'name': 'test-role-1',
            'description': 'Testing Role 1',
            'is_enabled': True
        })
        role_instance_2 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe6',
            'name': 'test-role-2',
            'description': 'Testing Role 2',
            'domain_id': 'test_domain_id',
            'is_enabled': True
        })
        role_instance_3 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe5',
            'name': 'test-role-3',
            'description': 'Testing Role 3',
            'is_enabled': True
        })
        # Mock find user response
        mock_connection().identity.find_user = \
            mock.MagicMock(return_value=user_instance_1)

        # Mock find role response
        mock_connection().identity.find_role = \
            mock.MagicMock(side_effect=[role_instance_1,
                                        role_instance_2,
                                        role_instance_3])

        project_instance = OpenstackProject(client_config=self.client_config)
        project_instance.resource_id = 'a95b5509-c122-4c2f-823e-884bb559afe9'

        # Call start project
        project._assign_users(project_instance, self.users)

    def test_validate_groups(self, mock_connection):
        # Prepare the context for start operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        group_instance_1 = openstack.identity.v3.group.Group(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'group-1',
            'description': 'old_description',
            'domain_id': 'test_domain_id',
        })
        role_instance_1 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe7',
            'name': 'test-role-1',
            'description': 'Testing Role 1',
            'is_enabled': True
        })
        role_instance_2 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe6',
            'name': 'test-role-2',
            'description': 'Testing Role 2',
            'domain_id': 'test_domain_id',
            'is_enabled': True
        })
        role_instance_3 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe5',
            'name': 'test-role-3',
            'description': 'Testing Role 3',
            'is_enabled': True
        })
        # Mock find group response
        mock_connection().identity.find_group = \
            mock.MagicMock(return_value=group_instance_1)

        # Mock find role response
        mock_connection().identity.find_role = \
            mock.MagicMock(side_effect=[role_instance_1,
                                        role_instance_2,
                                        role_instance_3])

        # Call start project
        project._validate_groups(self.client_config, self.groups)

    def test_assign_groups(self, mock_connection):
        # Prepare the context for start operation
        self._prepare_context_for_operation(
            test_name='ProjectTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        group_instance_1 = openstack.identity.v3.group.Group(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
            'name': 'group-1',
            'description': 'old_description',
            'domain_id': 'test_domain_id',
        })
        role_instance_1 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe7',
            'name': 'test-role-1',
            'description': 'Testing Role 1',
            'is_enabled': True
        })
        role_instance_2 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe6',
            'name': 'test-role-2',
            'description': 'Testing Role 2',
            'domain_id': 'test_domain_id',
            'is_enabled': True
        })
        role_instance_3 = openstack.identity.v2.role.Role(**{
            'id': 'a95b5509-c122-4c2f-823e-884bb559afe5',
            'name': 'test-role-3',
            'description': 'Testing Role 3',
            'is_enabled': True
        })
        # Mock find group response
        mock_connection().identity.find_group = \
            mock.MagicMock(return_value=group_instance_1)

        # Mock find role response
        mock_connection().identity.find_role = \
            mock.MagicMock(side_effect=[role_instance_1,
                                        role_instance_2,
                                        role_instance_3])

        project_instance = OpenstackProject(client_config=self.client_config)
        project_instance.resource_id = 'a95b5509-c122-4c2f-823e-884bb559afe9'

        # Call start project
        project._assign_groups(project_instance, self.groups)
