#!/usr/bin/env python

from __future__ import print_function
import hide

message = '''This will be my first covert message. it contains only printable
characters. (i'm going to include newlines in that statement. idk if newlines
actually qualify as `printable`, but whatever).'''

if __name__ == '__main__':
    img = hide.generate_image()

    img = hide.store(img, message)

    with open('test.out.jpg', 'w') as file:
        file.write(img)

    exit()

    with open('test.out.jpg', 'w') as file:
        img = file.read()

    message = hide.retrieve(img)

    print(message)
