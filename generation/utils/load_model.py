from preprocessing.text_to_speech import Xtts, Bark, Tacotron, MicroTts, Vall


class PreloadModel():
    def __init__(self, device) -> None:
        self.device = device

    @property
    def load(self):
        models_to_load = {
            "Xtts": Xtts,
            "Bark": Bark,
            "Tacotron": Tacotron,
            "MicroTts": MicroTts,
            "Vall": Vall
        }

        loaded_models = {}

        for name, model_class in models_to_load.items():
            loaded_models[name] = model_class(self.device)
            print(f"...load {name} done!")
        
        return loaded_models

"""
class PreloadModel():
    def __init__(self, devices) -> None:
        self.devices = devices

        self.models_to_load = {
            "Xtts": Xtts,
            "Bark": Bark,
            "Tacotron": Tacotron,
            "MicroTts": MicroTts,
            "Vall": Vall
        }

    def load(self, model_names):
        loaded_models = {}

        for name in model_names:
            if name in self.models_to_load:
                model_class = self.models_to_load[name]
                device = self.devices.get(name, "cuda:0")
                loaded_models[name] = model_class(device)
                print(f"...load {name} done!")
            else:
                print(f"Model {name} not found!")

        return loaded_models

"""
