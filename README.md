# Workorder

Simple distributed multiprocessing for Python

## Preparation

### Prepare nodes

Prepare n machines installed python 3.7

Notes:

```
# create digitalocean droplet
doctl compute droplet create node-1 --size 1gb --region sgp1 --image centos-7-x64

# show available droplets
doctl compute droplet list
```

### Run `agent.sh` in all nodes

```
python3 agent.py
```

## Example

See `example.py`