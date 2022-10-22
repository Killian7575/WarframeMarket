import pickle

def pickleSave(object, name, folder='.', silent=False):

    filename = folder + '/' + name + '.pkl'
    if silent==False:
        print('Saving object {} to pickle file {}'.format(name, filename))
    with open(filename, mode='wb') as fipkl:    
        pickle.dump(object, fipkl)
        
def pickleLoad(name, folder: str, silent=False):
    
    filename = folder + '/' + name + '.pkl'
    if silent==False:
        print('Loading object {} from pickle file {}'.format(name, filename))
    
    try:
        with open(filename, mode='rb') as fipkl:
            myObject=pickle.load(fipkl)
        return myObject
    except IOError:
        print('Pickle file {} not found, returning None object'.format(filename))
        return None



def pickleSaveOld(object, name, uri: str):

    #filename = uri + '/pkl/' + name + '.pkl'
    filename = name + '.pkl'
    with open(filename, mode='wb+') as fipkl:    
        pickle.dump(object, fipkl)
    print('{} saved as pkl file in {}'.format(name, filename))