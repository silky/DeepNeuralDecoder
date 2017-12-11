import numpy as np

class Spec:

    def __init__(self):

        self.num_qubit= 7
        self.syn_size= 3
        self.num_syn= 4
        self.input_size= 12
        self.num_labels= 2

        self.num_epochs= 2
        self.lstm_input_size= 6

        self.err_keys= ['errX3','errX4', 'errZ3', 'errZ4']
        self.syn_keys= ['synX12', 'synX34', 'synZ12', 'synZ34']
        self.perp_keys= [('errX3', 'errZ3'), ('errX4', 'errZ4')]

        #-- The 7 qubit CSS code generator --#

        self.L= {}
        for key in self.err_keys:
            self.L[key]= np.matrix([\
            [1,1,1,1,1,1,1]]).astype(np.int8)

        self.G= {}
        for key in self.err_keys:
            self.G[key] = np.matrix([ \
                [0,0,0,1,1,1,1], \
                [0,1,1,0,0,1,1], \
                [1,0,1,0,1,0,1]]).astype(np.int8)

        self.T= {}
        for key in ['errX3','errX4']:
            self.T[key]= np.matrix([\
                [0,0,0,1,0,0,0], \
                [0,1,0,0,0,0,0], \
                [1,0,0,0,0,0,0]]).astype(np.int8)

        for key in ['errZ3', 'errZ4']:
            self.T[key]= np.matrix([\
                [0,0,1,0,0,0,1], \
                [0,0,0,0,1,0,1], \
                [0,0,0,0,0,1,1]]).astype(np.int8)

        self.correctionMat= {}
        for key in self.err_keys:
            self.correctionMat[key] = np.matrix([ \
                [0,0,0,0,0,0,0], \
                [1,0,0,0,0,0,0], \
                [0,1,0,0,0,0,0], \
                [0,0,1,0,0,0,0], \
                [0,0,0,1,0,0,0], \
                [0,0,0,0,1,0,0], \
                [0,0,0,0,0,1,0], \
                [0,0,0,0,0,0,1]]).astype(np.int8)