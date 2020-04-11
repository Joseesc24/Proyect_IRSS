def generate_random_id():
    import random
    return '%032x' % random.getrandbits(256)


print(generate_random_id())
