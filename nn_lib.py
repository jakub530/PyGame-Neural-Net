
class node:
    def __init__(self):
        pass

class layer:
    def __init__(self, size):
        self.size = size 
        self.nodes = []
        self.init_nodes()

    def init_nodes(self):
        for ind in range(self.size):
            self.nodes.append(node())


class nn:
    def __init__(self, h_layers, inputs, outputs):
        init_layers(h_layers, inputs, outputs, layer)

    def init_layers(self, h_layers, inputs, outputs, layer_type):
        self.layers = [layer_type(inputs)]
        if isinstance(h_layers, int):
            h_layers = [h_layers]
        for layer_size in h_layers:
            self.layers.append(layer_type(layer_size))
        self.layers.append(layer_type(outputs))
        self.layer_number = len(self.layers)