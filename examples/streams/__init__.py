from amalfi.stream import stream


def main():
    s = stream(range(10)).map(lambda x: x * 2)
    print(s)


if __name__ == "__main__":
    main()
