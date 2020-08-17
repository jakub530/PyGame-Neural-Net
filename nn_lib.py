import random
import numpy as np
import math
import copy

class node:
    def __init__(self):
        pass

    def gen_weight(self):
        return (random.random()-0.5)*2

    def init_weights(self, size):
        self.weights = np.array([self.gen_weight() for i in range(size)])
        self.bias = self.gen_weight() * 0.01

    def activation_function(self, inp):
        try:
            return (math.exp(inp)-math.exp(-inp))/(math.exp(inp)+math.exp(-inp))
        except:
            print(inp)
        #return math.exp(inp)/(1+math.exp(inp))-0.5

    def propagate_value(self,inp):
        #bias = np.array([1])
        #full_inp = np.hstack((inp, bias))
        val = np.dot(self.weights,inp) + 1 * self.bias
        return self.activation_function(val)

    def find_output(self,inp):
        #bias = np.array([1])
        #full_inp = np.hstack((inp, bias))
        val = np.dot(self.weights,inp) + 1 * self.bias
        return self.activation_function(val)

    def modify_weights(self):
        learning_rate = 0.1
        mod = np.random.uniform(-learning_rate,learning_rate,self.weights.size)
        mod_bias = np.random.uniform(-learning_rate/100,learning_rate/100)
        self.bias += mod_bias
        self.weights += mod

class layer:
    def __init__(self, size):
        self.size = size 
        self.nodes = []
        self.init_nodes()

    def init_nodes(self):
        for ind in range(self.size):
            self.nodes.append(node())
    
    def init_weights(self, size):
        for node in self.nodes:
            node.init_weights(size)

    def propagate_value(self, inp):
        output = [node.propagate_value(inp) for node in self.nodes]
        return output

    def find_output(self, inp):
        output = [node.find_output(inp) for node in self.nodes]
        return output
        
    def modify_weights(self):
        for node in self.nodes:
            node.modify_weights()

class nn:
    def __init__(self, h_layers, inputs, outputs, init_weights = True):
        self.init_layers(h_layers, inputs, outputs, layer)
        if init_weights:
            self.init_weights()

    def init_layers(self, h_layers, inputs, outputs, layer_type):
        self.layers = [layer_type(inputs)]
        if isinstance(h_layers, int):
            h_layers = [h_layers]
        for layer_size in h_layers:
            self.layers.append(layer_type(layer_size))
        self.layers.append(layer_type(outputs))
        self.layer_number = len(self.layers)

    def init_weights(self):
        for ind,layer in enumerate(self.layers[1:]):
            layer.init_weights(self.layers[ind].size)

    def calculate_output(self, inp):
        all_values = []
        values = inp.copy()
        all_values.append(list(values.copy()))
        for layer in self.layers[1:]:
            values = layer.propagate_value(values)
            all_values.append(values.copy())
        #values = self.layers[-1].find_output(values)
        #all_values.append(values.copy())
        return values, all_values

    def modify_weights(self):
        for layer in self.layers[1:]:
            layer.modify_weights()

    def extract_weights(self):
        weight_list = []
        for layer in self.layers[1:]:
            layer_list = []
            for node in layer.nodes:
                node_list = node.weights
                layer_list.append(node_list)
            weight_list.append(layer_list)
        return weight_list

class nn_generation:
    def __init__(self, h_layers, inputs, outputs, inst_count):
        self.instances = []
        for ind in range(inst_count):
            self.instances.append(nn(h_layers, inputs, outputs))

    def retrain_nn(self, best):
        best_shortlist = best[0:19]

        for ind in range(len(self.instances)):
            if ind in best_shortlist:
                pass
            else:
                self.instances[ind] = copy.deepcopy(self.instances[random.choice(best_shortlist)])
                self.instances[ind].modify_weights()
        



class nn_tmp:
    def __init__(self, h_layers, inputs, outputs, inst_count, model_values):
        self.generations = [nn_generation(h_layers, inputs, outputs, inst_count)]
        self.model_values = model_values



    def get_model_values(self):
        return model_values
            

if __name__ == "__main__":
    inputs = 2
    hidden_layers = [2,2]
    outputs = 1

    nn_obj = nn_tmp(hidden_layers, inputs, outputs, 20)
    #my_nn = nn(hidden_layers, inputs, outputs)
    #my_nn.init_weights()
    #my_new_nn = copy.deepcopy(my_nn)
    #output, all_values = my_nn.calculate_output(np.array([1,3]))
    #weights = my_nn.extract_weights()
    #print(output)
    #for i in range(1000):
    #    my_nn.modify_weights()
    #    output, all_values = my_nn.calculate_output(np.array([1,3]))
    #    print(output)
    print("Tested")
    #pass