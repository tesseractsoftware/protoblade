from protoblade import  blade
from protoblade.cad import DomainCreator
from protoblade.cli import create_parser


def main(fname,output_filename=None):

    if not output_filename:
        output_filename = fname.replace('.toml', '.step')

    turbine = blade.Blade.from_config(fname)

    creator = DomainCreator(turbine)
    creator.create_domain()
    creator.export('domain',output_filename)


if __name__=="__main__":
    args = create_parser().parse_args()
    main(args.filepath)