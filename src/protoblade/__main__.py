from protoblade.machine import Machine
from protoblade.cad import DomainCreator
from protoblade.cli import create_parser


def main(fname, output_filename=None):
    if not output_filename:
        output_filename = fname.replace('.toml', '.step')

    machine = Machine.from_config_file(fname)

    for stage in machine.stages:
        for blade_def in stage.blades:
            if isinstance(output_filename,str):
                temp_out_fname = output_filename.replace('.step', f'-{stage.name}-{blade_def.name}.step')
            else:
                temp_out_fname = output_filename.name.replace('.step', f'-{stage.name}-{blade_def.name}.step')

            creator = DomainCreator(blade_def, stage.endwalls,machine.units,machine.axis)
            creator.create_domain()
            creator.export('domain', temp_out_fname)


if __name__ == "__main__":
    args = create_parser().parse_args()
    main(args.filepath)
