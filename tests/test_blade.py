from protoblade import geom,blade
def test_create_sections_from_2D_profile(vki_files):
    ps_pnts = geom.load_curves_from_fpd(vki_files['pressure'])
    ss_pnts = geom.load_curves_from_fpd(vki_files['suction'])

    N_sections = 3

    r_min = 0.25500
    r_max = 0.29000
    N_resample = 100
    ps_section,ss_section = blade.create_sections_from_2D_profile(ps_pnts,ss_pnts,N_sections,(r_min,r_max),n_resample=N_resample)

    assert len(ps_section)==len(ss_section)==N_sections

    #for sec_ps,sec_ss in zip(ps_section,ss_section):
    #    assert sec_ps.shape == (N_resample,)
    #    assert sec_ss.shape == (N_resample,)

    export = False
    if export:
        import numpy as np
        np.save('vki_ps',ps_section)
        np.save('vki_ss',ss_section)
        for fname,sections in  [('vki_ps.fpd',ps_section),('vki_ss.fpd',ss_section)]:
            with open(fname,'w+') as f:
                f.write(f'{sections[0].shape[0]} {N_sections}\n')
                for section in sections:
                    for i in range(section.shape[0]):
                        f.write(f"{section[i]['x']} {section[i]['y']} {section[i]['z']}\n")






