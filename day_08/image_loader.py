from typing import List


class Image:

    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.layers: List[List[int]] = []

    @classmethod
    def from_file(cls, filename: str, width: int, height: int) -> "Image":
        data = []
        with open(filename) as f:
            for line in f:
                data += cls.str_to_data(line)

        return cls.load(data, width, height)

    @classmethod
    def str_to_data(cls, data_str: str) -> List[int]:
        return [
            int(c)
            for c in data_str
        ]

    @classmethod
    def load(cls, data: List[int], width: int, height: int) -> "Image":
        raster_size = width * height
        if len(data) % raster_size != 0:
            raise RuntimeError('Wrong size')

        img = cls(width, height)

        current_offset = 0
        while current_offset + raster_size <= len(data):
            img.layers.append(data[current_offset:current_offset + raster_size])
            current_offset += raster_size

        return img

    def analyse(self) -> int:
        count_data = []
        for l_data in self.layers:
            layer_count = {
                0: 0,
                1: 0,
                2: 0,
            }
            for d in l_data:
                if d in layer_count:
                    layer_count[d] += 1

            if layer_count[0] > 0:
                # Ignore layers that don't have 0
                count_data.append(layer_count)

        print(f'Found {len(count_data)} layers with 0')

        # Take the layer with the fewest 0s
        least_zero = sorted(count_data, key=lambda d: d[0])[0]
        return least_zero[1] * least_zero[2]

    def merge_layers(self) -> List[str]:
        result = [p for p in self.layers[0]]

        for l_data in self.layers[1:]:
            for i, p in enumerate(l_data):
                if result[i] == 2:
                    # Transparent so we take the current value
                    result[i] = p

        #

        return self.data_as_str(result)

    def data_as_str(self, data: List[int]) -> List[str]:
        return [
            ''.join(map(str, data[h * self.width: (h + 1) * self.width]))
            for h in range(0, self.height)
        ]


if __name__ == '__main__':

    image = Image.from_file('input.txt', 25, 6)

    print(f'Loaded an image that has {len(image.layers)} {image.width}x{image.height} layers')
    check = image.analyse()
    print(f'Checkpickels is {check}')  # 2250

    rv = image.merge_layers()

    print(f'Message:')
    for l in rv:
        # To help reading we replace 0 by space
        l = l.replace('0', ' ')
        print(f'{l}')  # Can't do \n in fstring?

    # FHJUL
