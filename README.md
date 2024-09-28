![img](img/example.png)

# Radium Nodes

A no frills, vertical node-graph editor for PySide6. 

⚠️`This project is currently in active development and a concrete API is not yet defined.`

## Demo Application

A demo application demonstrating the API is provided as part of the package, and can be started using the `radium-demo`
command.

```bash
pip install -e.
radium-demo
```

It can also be invoked via python. This creates a QApplication and a QMainWindow so it should not be invoked from within
an existing QT Application.

```python
from radium.demo.__main__ import main
main()
```

## Roadmap

### Essential

- [X] Demo Application
- [X] Undo/Redo.
- [X] Serialization.
- [X] Node Browser.
- [ ] Node Parameters.
- [ ] Node Groups & Gizmos
- [ ] Graph Events or Signals
- [ ] Documentation

### Nice to have
- [X] Custom Node / Port Coloring
- [ ] Custom Node / Port Drawing.

