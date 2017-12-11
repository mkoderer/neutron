# Copyright 2017 SAP SE
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron import context as c
from neutron.plugins.ml2 import driver_api as api

from neutron_lib.plugins import directory
from oslo_log import log

LOG = log.getLogger(__name__)


class AclLBPortBlockDriver(api.MechanismDriver):
    @property
    def _plugin(self):
        return directory.get_plugin()

    def __init__(self):
        LOG.debug("ACL LB mechanism driver initializing...")
        super(AclLBPortBlockDriver, self).__init__()
        LOG.debug("ACL LB mechanism driver initializing.")

    def initialize(self):
        pass

    def delete_port_precommit(self, context):
        if ('neutron:LOADBALANCERV2' ==
            context.current['device_owner']):
            LOG.debug("LB port is about to be deleted"
                      "- will be reserved (Port_id: %(port)s)",
                      {'port': context.current['id']})

    def delete_port_postcommit(self, context):
        old_port = context.current
        if ('neutron:LOADBALANCERV2' ==
                old_port['device_owner']):
            admin_context = c.get_admin_context()
            port_data = {
                'tenant_id': old_port['tenant_id'],
                'name': 'blocked-' + old_port['id'],
                'network_id': old_port['network_id'],
                'admin_state_up': False,
                'device_owner': "RESERVED",
                'device_id': old_port['device_id'],
                'fixed_ips': old_port['fixed_ips']
            }
            port = self._plugin.create_port(admin_context, {'port': port_data})
            LOG.debug("Reserved/blocked port (Port_id: %(port)s)",
                {'port': port['id']})
