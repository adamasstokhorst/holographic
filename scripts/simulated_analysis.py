"""
Performs many simulations on specified images, and saves the calculated data
in `plot_data/`.
"""

import holographic as hl
import ScriptHelper as Sh


if __name__ == '__main__':
    # --- PARAMETERS THAT MAY BE CHANGED ---
    # list of filepaths
    fnames = ['control/offering.jpg']

    # parameters
    big_m = 64
    small_m = 8
    big_n = 8
    sigma = 0.01
    mode = 1

    # number of combinations to sample
    buildup_limit = 25
    sampling_limit = float('inf')

    # --- END OF PARAMETERS, BEGIN CODE ---
    handler = hl.ImageHandler

    print 'Calculating simulated recovery results...'
    print '  Parameters: M={}, m={}, N={}, sigma^2={} on mode {}'.format(big_m, small_m, big_n, sigma, mode)

    params = {'big_m': big_m, 'small_m': small_m, 'big_n': big_n, 'sigma': sigma}

    # Prepare all the parameters
    param_dict = {'aggregate': Sh.load_data('aggregate_statistics', params)}
    param_dict['aggregate']['partitions'] = param_dict['aggregate']['partitions'][mode]
    param_dict['aggregate'].update(params)

    param_dict['grid'] = dict(param_dict['aggregate'])
    param_dict['grid']['lamda'], param_dict['grid']['psi'] = hl.statistic.get_lp_lambda(1, big_m)
    param_dict['grid']['partitions'] = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma,
                                                                        param_dict['grid']['lamda'], mode=mode)

    param_dict['line'] = dict(param_dict['aggregate'])
    param_dict['line']['lamda'], param_dict['line']['psi'] = hl.statistic.get_lp_lambda(2, big_m)
    param_dict['line']['partitions'] = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma,
                                                                        param_dict['line']['lamda'], mode=mode)

    params['mode'] = mode

    for fname in fnames:
        # make a copy for image-specific statistics
        param_dict['img'] = dict(param_dict['aggregate'])
        param_dict['img']['lamda'], param_dict['img']['psi'] = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fname)
        param_dict['img']['partitions'] = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma,
                                                                           param_dict['img']['lamda'], mode=mode)
        
        Sh.simulation_calc(params, param_dict, fname, handler, buildup_limit, sampling_limit, buildup=True)
        Sh.simulation_calc(params, param_dict, fname, handler, buildup_limit, sampling_limit, overall=True)
