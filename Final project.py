import docker
import time

#question  1 
client = docker.from_env()

swarmId = client.swarm.init(
            advertise_addr='127.0.0.1',
            listen_addr='0.0.0.0:5000',
            force_new_cluster=False, 
            default_addr_pool=['10.20.0.0/16'],
            subnet_size=24, 
           )
print("\nSwarm")
print("swarm ID: ", client.swarm.id)
print("swarm Name: ", client.swarm.attrs['Spec']['Name'])
print("swarm Created Date: ", client.swarm.attrs['CreatedAt'])


ipam_pool = docker.types.IPAMPool(
    subnet='10.10.10.0/24',
    gateway='10.10.10.254'
)

ipam_config = docker.types.IPAMConfig(
    pool_configs=[ipam_pool]
)


client.networks.create(
            "se443_test_net",
            driver="overlay",
            scope="global",
            ipam=ipam_config
        )
print("\nNetwork")
print("network ID", client.networks.get('se443_test_net').id)
print("network Name", client.networks.get('se443_test_net').attrs['Name'])
print("network Create Date", client.networks.get('se443_test_net').attrs['Created'])
  
service = client.services.create(
    "eclipse-mosquitto",
    name="broker",
    restart_policy=docker.types.RestartPolicy(condition="any")
).scale(3)

print("\nBroker")
print("Broker service deployed with ID: ", client.services.list()[0].id)
print("Broker service name: ", client.services.list()[0].name)
print("Broker service replicas: ", client.services.list()[0].attrs['Spec']['Mode']['Replicated']['Replicas'])
print("Broker service Creation date  : ", client.services.list()[0].attrs['CreatedAt'])


#question 2

client.services.create("efrecon/mqtt-client", name="Subscriber",  restart_policy=docker.types.RestartPolicy(condition="any"), networks=["se443_test_net"], command='sub -h host.docker.internal -t alfaisal_uni -v').scale(3)
print("\nSubscriber")
print("Subscriber service deployed with ID ",client.services.list()[0].id)
print("Subscriber Name: ",client.services.list()[0].name)
print("Subscriber Num Of Replicas: ",client.services.list()[0].attrs['Spec']['Mode']['Replicated']['Replicas'])



client.services.create("efrecon/mqtt-client", name="Publisher",  restart_policy={"Name": "always"}, networks=["se443_test_net"], command='pub -h host.docker.internal -t alfaisal_uni -m "sara aldrees"').scale(3)
print("\nPublisher")
print("Publisher service deployed with ID ", client.services.list()[0].id)
print("Publisher service Name: ", client.services.list()[0].name)
print("Publisher service Num Of Replicas: ", client.services.list()[0].attrs['Spec']['Mode']['Replicated']['Replicas'])


#question 3

time.sleep(300)

print("\nRemoving Publisher", end="")
client.services.get("Publisher").remove()
print("Removed ")


print("\nRemoving Subscribe", end="")
client.services.get("Subscriber").remove()
print("Removed ")


print("\nRemoving Broker", end="")
client.services.get("Broker").remove()
print("Removed ")


print("\nRemoving Network", end="")
client.networks.get("se443_test_net").remove()
print("Removed ")


print("\nRemoving Swarm", end="")
client.swarm.leave(force=True)
print("Removed ")