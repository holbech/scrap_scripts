#!/usr/bin/env python
import os
import subprocess
import sys
import tempfile
import urllib

import boto.ec2
from boto.utils import get_instance_metadata

if __name__ == "__main__":

    conn = boto.ec2.connect_to_region("eu-west-1")
    instance_id = get_instance_metadata(timeout=1, num_retries=3)['instance-id']
    tags = conn.get_all_reservations(instance_ids=[instance_id])[0].instances[0].tags
    
    def get_config_server():
        my_name = tags.get('Name','').split('.')
        if len(my_name) == 3 and len(my_name[1]) == 3 and my_name[2].startswith('mojn'):
            #TODO: Should be made general once zookeeper-naming is consistent across environments
            if my_name[1] == 'stg':
                return 'zookeeper-001a.stg.mojn001.mojn001.internal.ops.mojn.com'
            if my_name[1] == 'prd':
                return 'zookeeper-cluster001-001a.prd.mojn001.internal.ops.mojn.com'
        return ''

    def get_exe(my_name=''):
        zk_path = tags.get('config-server', get_config_server())
        assert zk_path, 'No config-server tag specified and none could be derived from Name tag'
        zk_command = 'get /mojn/running-builds/' + (my_name or tags.get('Name', instance_id))
        with tempfile.NamedTemporaryFile(delete=True) as command_file:
            command_file.write(zk_command + '\n')
            command_file.flush()
            results = subprocess.check_output('/home/ec2-user/zk/bin/zkCli.sh -server %s < %s' % (zk_path, command_file.name), shell=True, stderr=subprocess.STDOUT)
        images = [ l.strip() for l in results.splitlines() if l.count(':') == 1 and urllib.quote(l, ':') == l ]
        assert images, 'No docker images in output: ' + results
        assert len(images) == 1, 'Too many possible docker images in output: ' + ', '.join(images)
        dns_search_path = zk_path.partition('.')[2]
        if dns_search_path:
            dns_search_path = '--dns-search=' + dns_search_path
        dns_search_path += ' --dns-search=internal.ops.mojn.com --dns=172.16.0.23'
        return 'docker run %s -v /srv/tmp:/tmp havnearbejder.mojn.com:443/mojn/%s' % (dns_search_path, images[0])
    
    def get_standard_run_args():
        result = tags.get('standard-run', '').split()
        return result

    args = sys.argv[1:]
    if len(args) < 2:
        args = get_standard_run_args()
    if not args:
        print "Nothing done"
    else:
        subprocess.check_call(get_exe(args[0]) + ' '.join([''] + args[1:]), shell=True)
        