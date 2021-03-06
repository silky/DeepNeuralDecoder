# ------------------------------------------------------------------------------
#
# MIT License
#
# Copyright (c) 2018 Pooya Ronagh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ------------------------------------------------------------------------------

import sys, os, json
from time import time, strftime, localtime
import cPickle as pickle
from ModelExRecCNOT import *
from ModelSurface1EC import *
from HyperTune import BayesOptTest

def run_hypertune(spec, param, hyperparam):

    filename= hyperparam['env']['filename']
    with open(param['env']['pickle folder'] + filename, 'rb') as input_file:
        start_time= time()
        print('Pickling model from ' + \
            param['env']['pickle folder'] + filename + ' ...'),
        m = pickle.load(input_file)
        print('Done in ' + '{0:.2f}'.format(time() - start_time) + 's.')

    m.test_size= int(param['data']['test fraction'] * m.data_size)
    m.train_size= m.data_size - m.test_size
    m.num_batches= m.train_size // param['opt']['batch size']
    m.spec= spec

    engine = BayesOptTest(m, param, hyperparam)
    mvalue, x_out, error = engine.optimize()
    print('### Best value: ' + str(mvalue))
    print('### Best query: ' + ' '.join(str(x) for x in x_out))

    outfilename = strftime("%Y-%m-%d-%H-%M-%S", localtime())
    f = open(param['env']['param folder'] + outfilename + '.json', 'w')
    f.write(json.dumps(engine.best_param, indent=2))
    f.close()

def run_pickler(spec, param):

    for filename in sorted(os.listdir(param['env']['raw folder'])):

        with open(param['env']['pickle folder'] + \
            filename.replace('.txt', '.pkl'), "wb") as output_file:
            print("Reading data from " + filename)
            if (param['env']['look up']):
                if (param['env']['FT scheme']=='ExRecCNOT'):
                    model= LookUpExRecCNOT(\
                        param['env']['raw folder']+ filename, spec)
                elif (param['env']['FT scheme']=='Surface1EC'):
                    model= LookUpSurface1EC(\
                        param['env']['raw folder']+ filename, spec)
                else:
                    raise ValueError('Unknown look up model requested.')
            else:
                if (param['env']['FT scheme']=='ExRecCNOT'):
                    model= PureErrorExRecCNOT(\
                        param['env']['raw folder']+ filename, spec)
                elif (param['env']['FT scheme']=='Surface1EC'):
                    model= PureErrorSurface1EC(\
                        param['env']['raw folder']+ filename, spec)
                else:
                    raise ValueError('Unknown pure error model requested.')
            pickle.dump(model, output_file)

def run_benchmark(spec, param, f0= None, f1= None, save= False):

    output= []
    for filename in sorted(os.listdir(param['env']['pickle folder']))[f0:f1]:

        with open(param['env']['pickle folder'] + filename, 'rb') as input_file:
            start_time= time()
            print('Pickling model from ' + \
                param['env']['pickle folder'] + filename + ' ...'),
            m = pickle.load(input_file)
            print('Done in ' + '{0:.2f}'.format(time() - start_time) + 's.')

        if 'total fraction' in param['data']:
            m.data_size= int(param['data']['total fraction'] * m.data_size) 
            print('Fraction training on ' + str(m.data_size) + ' rows.')
        m.test_size= int(param['data']['test fraction'] * m.data_size)
        m.train_size= m.data_size - m.test_size
        m.num_batches= m.train_size // param['opt']['batch size']
        m.spec= spec

        fault_rates= []
        for i in range(param['data']['num trials']):
            if (param['nn']['iso']):
                prediction, test_beg= m.iso_train(param)
            elif (param['nn']['mixed']):                
                prediction, test_beg= m.mixed_train(param)
            else:
                if save:
                    outfilename = strftime("%Y-%m-%d-%H-%M-%S", localtime())
                    prediction, test_beg= m.train(param, save= True, save_path=\
                        param['env']['report folder'] + outfilename + '.ckpt')
                else:
                    prediction, test_beg= m.train(param)
            print('Testing ...'),
            start_time= time()
            result= m.num_logical_fault(prediction, test_beg)
            print('Done in ' + '{0:.2f}'.format(time() - start_time) + 's.')
            print('Result= ' + str(m.error_scale * result))
            fault_rates.append(m.error_scale * result)

        run_log= {}
        run_log['data']= {}
        run_log['opt']= {}
        run_log['res']= {}
        run_log['param']= param
        run_log['data']['path']= filename
        run_log['data']['fault scale']= m.error_scale
        run_log['data']['total size']= m.total_size
        run_log['data']['test size']= m.test_size
        run_log['data']['train size']= m.train_size
        run_log['opt']['batch size']= param['opt']['batch size']
        run_log['opt']['number of batches']= m.num_batches
        run_log['res']['p']= m.p
        run_log['res']['lu avg']= m.lu_avg
        run_log['res']['lu std']= m.lu_std
        run_log['res']['nn res'] = fault_rates
        run_log['res']['nn avg'] = np.mean(fault_rates)
        run_log['res']['nn std'] = np.std(fault_rates)
        output.append(run_log)

    outfilename = strftime("%Y-%m-%d-%H-%M-%S", localtime())
    f = open(param['env']['report folder'] + outfilename + '.json', 'w')
    f.write(json.dumps(output, indent=2))
    f.close()

if __name__=='__main__':

    with open(sys.argv[2]) as paramfile:
        param = json.load(paramfile)

    if(param['env']['EC scheme']=='SurfaceD3'):
        import _SurfaceD3Lookup as lookup 
    elif(param['env']['EC scheme']=='SurfaceD5'):
        import _SurfaceD5Lookup as lookup 
    elif(param['env']['EC scheme']=='ColorD3'):
        import _ColorD3Lookup as lookup 
    elif(param['env']['EC scheme']=='ColorD5'):
        import _ColorD5Lookup as lookup 
    else:
        raise ValueError('Unknown circuit type.')
    spec= lookup.Spec()

    if (sys.argv[1]=='gen'):
        run_pickler(spec, param)
    elif (sys.argv[1]=='bench'):
        if (len(sys.argv)>3):
            run_benchmark(spec, param, int(sys.argv[3]), int(sys.argv[4]))
        else: 
            run_benchmark(spec, param)
    elif (sys.argv[1]=='save'):
        run_benchmark(spec, param, \
            int(sys.argv[3]), int(sys.argv[4]), save= True)
    elif (sys.argv[1]=='tune'):
        with open(sys.argv[3]) as hyperparam:
            hyperparam = json.load(hyperparam)
        run_hypertune(spec, param, hyperparam)
    else:
        print('Error: Unrecognized command!')
