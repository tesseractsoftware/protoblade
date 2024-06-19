import argparse


def create_parser():
    parser = argparse.ArgumentParser(description=' Protoblade')
    parser.add_argument('filepath', help='Location of the input file.')
    return parser
