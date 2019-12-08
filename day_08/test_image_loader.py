from day_08.image_loader import Image


def test_load_image():
    img = Image.load(Image.str_to_data('123456789012'), 3, 2)

    assert len(img.layers) == 2
    assert img.layers[0] == Image.str_to_data('123456')
    assert img.layers[1] == Image.str_to_data('789012')


def test_check():
    img = Image.load(Image.str_to_data('123456712012'), 3, 2)

    assert len(img.layers) == 2

    assert img.analyse() == 4


def test_merge():
    img = Image.load(Image.str_to_data('0222112222120000'), 2, 2)

    assert len(img.layers) == 4

    assert img.layers[0] == Image.str_to_data('0222')
    assert img.layers[1] == Image.str_to_data('1122')
    assert img.layers[2] == Image.str_to_data('2212')
    assert img.layers[3] == Image.str_to_data('0000')

    assert img.merge_layers() == [
        '01',
        '10',
    ]


def test_questions():
    image = Image.from_file('input.txt', 25, 6)
    assert image.analyse() == 2250

    rv = image.merge_layers()
    assert rv == [
        '1111010010001101001010000',
        '1000010010000101001010000',
        '1110011110000101001010000',
        '1000010010000101001010000',
        '1000010010100101001010000',
        '1000010010011000110011110',
    ]
