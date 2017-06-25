# PyBroker

Multi-agent simulation of stock exchange with bunch of broker agents


## Running SPADE server

```
configure.py localhost

runspade.py 127.0.0.1
```

## Simulation

In order to run run simulation in two separate terminal window run

```
python stock_exchange_agent.py
```

Note that agent that acts as stock exchange should be started first

```
python broker_agent.py
```