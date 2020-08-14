def generate_value():
    return random.random()

def mock_values(inp, hidden, output, rand = False):
    layers = [inp, *hidden, output]
    values = []
    for layer_ind in range(len(layers)-1):
        tmp_val_mid = []
        for prev_ind in range(layers[layer_ind]):
            tmp_val_bot = []
            for next_ind in range(layers[layer_ind+1]):
                val = generate_value()
                tmp_val_bot.append(val)
            tmp_val_mid.append(tmp_val_bot)
        values.append(tmp_val_mid)
    return values