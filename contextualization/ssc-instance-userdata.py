# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys
import inspect
from os import environ as env

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

flavor = 'ssc.xsmall' 
private_net = "UPPMAX 2021/1-5 Internal IPv4 Network"
floating_ip_pool_name = "Public External IPv4 Network"
floating_ip = None
image_name = 'Ubuntu 18.04'
loader = loading.get_plugin_loader('password')

auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                username=env['OS_USERNAME'],
                                password=env['OS_PASSWORD'],
                                project_name=env['OS_PROJECT_NAME'],
                                project_domain_name=env['OS_USER_DOMAIN_NAME'],
                                project_id=env['OS_PROJECT_ID'],
                                user_domain_name=env['OS_USER_DOMAIN_NAME'])

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
print ("user authorization completed.")

image = nova.glance.find_image(image_name)

flavor = nova.flavors.find(name=flavor)

if private_net != None:
    net = nova.neutron.find_network(private_net)
    nics = [{'net-id': net.id}]
else:
    sys.exit("private-net not defined.")

cfg_file_path =  os.getcwd()+'/cloud_cfg.txt'
if os.path.isfile(cfg_file_path):
    userdata = open(cfg_file_path)
    print("Cloud init file successfully set")
else:
    sys.exit("cloud-cfg.txt is not in current working directory")

secgroups = ['default','stefanos_sec_group']

print ("Creating instance ... ")
instance = nova.servers.create(name="stef_lab3", image=image, flavor=flavor, userdata=userdata, nics=nics,security_groups=secgroups, key_name="stefkeypair")
inst_status = instance.status
print ("waiting for 10 seconds.. ")
time.sleep(10)

while inst_status == 'BUILD':
    print ("Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more...")
    time.sleep(5)
    instance = nova.servers.get(instance.id)
    inst_status = instance.status

#instance.add_floating_ip("stef_context_vm1", floating_ip)
print ("Instance: "+ instance.name +" is in " + inst_status + "state")
if floating_ip_pool_name != None: 
    floating_ip = nova.floating_ips.create(floating_ip_pool_name)
else: 
    sys.exit("public ip pool name not defined.")
