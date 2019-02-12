# Workorder

Simple distributed multiprocessing for Python

## Preparation

### Prepare nodes

Prepare n machines installed python 3.7

Notes:
```
# create digitalocean droplet
doctl compute droplet create node-1 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-2 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-3 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-4 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-5 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-6 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-7 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-8 --size 1gb --region sgp1 --image ubuntu-16-04-x64
doctl compute droplet create node-9 --size 1gb --region sgp1 --image ubuntu-16-04-x64

# show available droplets
doctl compute droplet list
```

### Run `agent.sh` in all nodes

```
python3 -u agent.py > /var/log/workorder.log &
```

## Example

See `example.py`