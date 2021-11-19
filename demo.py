from simplepng import *

sources = [
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
]
img = Simplepng(sources, 4, 4, 'hello')
img.run()
