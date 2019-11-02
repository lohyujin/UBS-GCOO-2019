import os
import shutil

def regulation(array):
    #array = [currency, acc_name, ben_acc_no, ben_name, BIC, ben_address, PPC]
    country_code = array[3][4:6]
    if(array[0] == 'MYR'):
        a = array[1].replace(',', '')
        a = a.replace('\'', '')
        checks = a.split(' ')
        for check in checks:
            if(check in array[3]):
                return True
        return False
    elif(array[0] == 'CAD'):
        if(country_code == 'CA'):
            return array[5] != ''
    elif(country_code == 'AE'):
        return (array[4] != '')
    return True

def retrieve_files(folder, name):
    path = folder + "/" + name
    file_array = os.listdir(path)
    for i in range(len(file_array)):
        file_array[i] = path + "/" + file_array[i]
    return(file_array)

