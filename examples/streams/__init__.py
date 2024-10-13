from amalfi.stream import Stream


def main():
    stream = Stream(range(10)).map(lambda x: x * 2)
    print(stream)


if __name__ == "__main__":
    main()
