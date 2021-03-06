from custom_layers import Conv1D_zerophase_linear, Conv1D_linearphase, Conv1D_zerophase,\
    DCT1D, Conv1D_gammatone, Conv1D_linearphaseType, Attention
from keras.layers import Input, Conv1D, MaxPooling1D, Dense, Dropout, Flatten, Activation, AveragePooling1D
from keras import initializers
from keras.layers.normalization import BatchNormalization
from keras.layers.merge import Concatenate
from keras.models import Model
from keras.regularizers import l2
from keras.constraints import max_norm
from keras.optimizers import Adam, SGD # Nadam, Adamax
import numpy as np
import tables,h5py
from Gradient_Reverse_Layer import GradientReversal
from ResultAnalyser import Result
from utils import Confused_Crossentropy



def branch(input_tensor,num_filt,kernel_size,random_seed,padding,bias,maxnorm,l2_reg,
           eps,bn_momentum,activation_function,dropout_rate,subsam,trainable):

    num_filt1, num_filt2 = num_filt
    t = Conv1D(num_filt1, kernel_size=kernel_size,
                kernel_initializer=initializers.he_normal(seed=random_seed),
                padding=padding,
                use_bias=bias,
                kernel_constraint=max_norm(maxnorm),
                trainable=trainable,
                kernel_regularizer=l2(l2_reg))(input_tensor)
    t = BatchNormalization(epsilon=eps, momentum=bn_momentum, axis=-1)(t)
    t = Activation(activation_function)(t)
    t = Dropout(rate=dropout_rate, seed=random_seed)(t)
    t = MaxPooling1D(pool_size=subsam)(t)
    t = Conv1D(num_filt2, kernel_size=kernel_size,
               kernel_initializer=initializers.he_normal(seed=random_seed),
               padding=padding,
               use_bias=bias,
               trainable=trainable,
               kernel_constraint=max_norm(maxnorm),
               kernel_regularizer=l2(l2_reg))(t)
    t = BatchNormalization(epsilon=eps, momentum=bn_momentum, axis=-1)(t)
    t = Activation(activation_function)(t)
    t = Dropout(rate=dropout_rate, seed=random_seed)(t)
    t = MaxPooling1D(pool_size=subsam)(t)
    # t = Flatten()(t)
    return t

def heartnet(load_path,activation_function='relu', bn_momentum=0.99, bias=False, dropout_rate=0.5, dropout_rate_dense=0.0,
             eps=1.1e-5, kernel_size=5, l2_reg=0.0, l2_reg_dense=0.0,lr=0.0012843784, lr_decay=0.0001132885, maxnorm=10000.,
             padding='valid', random_seed=1, subsam=2, num_filt=(8, 4), num_dense=20,FIR_train=False,trainable=True,type=1,
             num_class=2, num_class_domain=1,hp_lambda=0,batch_size=1024,optim='SGD'):
    
    #num_dense = 20 default 
    input = Input(shape=(2500, 1))

    coeff_path = '../data/filterbankcoeff60.mat'
    coeff = tables.open_file(coeff_path)
    b1 = coeff.root.b1[:]
    b1 = np.hstack(b1)
    b1 = np.reshape(b1, [b1.shape[0], 1, 1])

    b2 = coeff.root.b2[:]
    b2 = np.hstack(b2)
    b2 = np.reshape(b2, [b2.shape[0], 1, 1])

    b3 = coeff.root.b3[:]
    b3 = np.hstack(b3)
    b3 = np.reshape(b3, [b3.shape[0], 1, 1])

    b4 = coeff.root.b4[:]
    b4 = np.hstack(b4)
    b4 = np.reshape(b4, [b4.shape[0], 1, 1])

    ## Conv1D_linearphase

    # input1 = Conv1D_linearphase(1 ,61, use_bias=False,
    #                 # kernel_initializer=initializers.he_normal(random_seed),
    #                 weights=[b1[30:]],
    #                 padding='same',trainable=FIR_train)(input)
    # input2 = Conv1D_linearphase(1, 61, use_bias=False,
    #                 # kernel_initializer=initializers.he_normal(random_seed),
    #                 weights=[b2[30:]],
    #                 padding='same',trainable=FIR_train)(input)
    # input3 = Conv1D_linearphase(1, 61, use_bias=False,
    #                 # kernel_initializer=initializers.he_normal(random_seed),
    #                 weights=[b3[30:]],
    #                 padding='same',trainable=FIR_train)(input)
    # input4 = Conv1D_linearphase(1, 61, use_bias=False,
    #                 # kernel_initializer=initializers.he_normal(random_seed),
    #                 weights=[b4[30:]],
    #                 padding='same',trainable=FIR_train)(input)

    ## Conv1D_linearphase Anti-Symmetric
    #
    input1 = Conv1D_linearphaseType(1 ,60, use_bias=False,
                    # kernel_initializer=initializers.he_normal(random_seed),
                    weights=[b1[31:]],
                    padding='same',trainable=FIR_train, type = type)(input)
    input2 = Conv1D_linearphaseType(1, 60, use_bias=False,
                    # kernel_initializer=initializers.he_normal(random_seed),
                    weights=[b2[31:]],
                    padding='same',trainable=FIR_train, type = type)(input)
    input3 = Conv1D_linearphaseType(1, 60, use_bias=False,
                    # kernel_initializer=initializers.he_normal(random_seed),
                    weights=[b3[31:]],
                    padding='same',trainable=FIR_train, type = type)(input)
    input4 = Conv1D_linearphaseType(1, 60, use_bias=False,
                    # kernel_initializer=initializers.he_normal(random_seed),
                    weights=[b4[31:]],
                    padding='same',trainable=FIR_train, type = type)(input)

    #Conv1D_gammatone

    # input1 = Conv1D_gammatone(kernel_size=81,filters=1,fsHz=1000,use_bias=False,padding='same')(input)
    # input2 = Conv1D_gammatone(kernel_size=81,filters=1,fsHz=1000,use_bias=False,padding='same')(input)
    # input3 = Conv1D_gammatone(kernel_size=81,filters=1,fsHz=1000,use_bias=False,padding='same')(input)
    # input4 = Conv1D_gammatone(kernel_size=81,filters=1,fsHz=1000,use_bias=False,padding='same')(input)

    t1 = branch(input1,num_filt,kernel_size,random_seed,padding,bias,maxnorm,l2_reg,
           eps,bn_momentum,activation_function,dropout_rate,subsam,trainable)
    t2 = branch(input2,num_filt,kernel_size,random_seed,padding,bias,maxnorm,l2_reg,
           eps,bn_momentum,activation_function,dropout_rate,subsam,trainable)
    t3 = branch(input3,num_filt,kernel_size,random_seed,padding,bias,maxnorm,l2_reg,
           eps,bn_momentum,activation_function,dropout_rate,subsam,trainable)
    t4 = branch(input4,num_filt,kernel_size,random_seed,padding,bias,maxnorm,l2_reg,
           eps,bn_momentum,activation_function,dropout_rate,subsam,trainable)

    merged = Concatenate(axis=-1)([t1, t2, t3, t4])
    # merged = DCT1D()(merged)
    merged = Flatten()(merged)
    # discriminator
    #dann_in = Attention(name='domain_att',trainable=False)(merged)
    #merged = Attention(name = 'class_att',trainable=False)(merged)
    dann_in = GradientReversal(hp_lambda=hp_lambda,name='grl')(merged)
    dsc = Dense(50,
                   activation=activation_function,
                   kernel_initializer=initializers.he_normal(seed=random_seed),
                   use_bias=bias,
                   kernel_constraint=max_norm(maxnorm),
                   kernel_regularizer=l2(l2_reg_dense),
                   name = 'domain_dense')(dann_in)   
    dsc = Dense(num_class_domain, activation='softmax', name = "domain")(dsc)          
    merged = Dense(num_dense,
                   activation=activation_function,
                   kernel_initializer=initializers.he_normal(seed=random_seed),
                   use_bias=bias,
                   kernel_constraint=max_norm(maxnorm),
                   kernel_regularizer=l2(l2_reg_dense),
                   name = 'class_dense')(merged)
    # merged = BatchNormalization(epsilon=eps,momentum=bn_momentum,axis=-1) (merged)
    # merged = Activation(activation_function)(merged)
    #merged = Dropout(rate=dropout_rate_dense, seed=random_seed)(merged)
    merged = Dense(num_class, activation='softmax', name="class")(merged)

    #model = Model(inputs=input, outputs=[merged,dsc])
    model = Model(inputs=input, outputs=[merged,dsc])

    if load_path:
        print("Load weights from ",load_path)
        model.load_weights(filepath=load_path, by_name=False)

    #if load_path:  # If path for loading model was specified
    #model.load_weights(filepath='../../models_dbt_dann/fold_a_gt 2019-09-09 16:53:52.063276/weights.0041-0.6907.hdf5', by_name=True)
    # models/fold_a_gt 2019-09-04 17:36:52.860817/weights.0200-0.7135.hdf5
    
    if optim=='Adam':
        opt = Adam(lr=lr, decay=lr_decay)
    else:  
        opt = SGD(lr=lr,decay=lr_decay)
    if(num_class_domain>1):
        domain_loss_function = 'categorical_crossentropy'
    else:
        domain_loss_function = 'binary_crossentropy'
    model.compile(optimizer=opt, loss={'class':'categorical_crossentropy','domain':domain_loss_function}, metrics=['accuracy'])
    #model.compile(optimizer=opt, loss=['categorical_crossentropy','categorical_crossentropy'], metrics=['accuracy'])
    
    return model

def getAttentionModel(model,foldname,lr,lr_decay):
    load_path = Result(foldname, find = True).df['model_path']
    load_path = load_path.replace(load_path[-16:-12],str(int(load_path[-16:-12])+1).rjust(4,'0'))

    model.load_weights(load_path)
    layers = {x.name:x for x in model.layers[-5:]}
    layers
    while('flatten' not in model.layers[-1].name):
        model.layers.pop()
    merged = Attention(name='att')(model.layers[-1].output)
    dann_in = layers['grl'](merged)
    dsc = layers['domain_dense'](dann_in)
    dsc = layers['domain'](dsc)
    merged = layers['class_dense'](merged)
    merged = layers['class'](merged)
    model = Model(inputs=model.layers[0].input, outputs=[merged,dsc])
    for layer in model.layers:
        if 'flatten' in layer.name:
            break
        else:
            layer.trainable = False
    opt = SGD(lr=lr,decay=lr_decay)

    model.compile(optimizer=opt, loss={'class':'categorical_crossentropy','domain':'categorical_crossentropy'}, metrics=['accuracy'])
    return model