# Defining Ports and Nodes

In order to have nodes in your graph you need to define and register them.

## Ports

Ports represent points of connection in the graph, each port has a direction and datatype which defines which 
other ports it can be connected to. There are 2 port directions `Output` and `Input` and any number of data types.

For 2 ports to be connected to each other they must share the same datatype and have different directions.


When defining a port type you can customise it in the following ways.

| property      | description                                                                      | required         |
|---------------|----------------------------------------------------------------------------------|------------------|
| datatype      | a unique name defining what sort of data this port handles, e.g. float           | :material-check: |
| fill color    | the ports fill color                                                             | :material-check: |
| outline color | an rgb color which will be used for the ports outline                            |                  |
| path          | an optional list of points used to define a custom port shape, defaults to a box |                  |


### Example
```python
image_port = PortType(
    datatype="image",
    fill_color=(127,127,12),    
)
```

## Nodes

### Example
```python
from radium.nodegraph.node_types.prototypes import NodeType

merge_node = NodeType(
    name="Merge",
    category="Nodes",
    inputs={
        "image_a": "image",
        "image_b": "image",
    },
)

```
