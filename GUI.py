from statistics import median
from cv2 import mean
from numpy import std
import detection_function
import cv2
from PIL import Image
import os
import pandas as pd
import random
import prepare_data
from way_2_model import Net
import torch
import torchvision.transforms as transforms
from data_set import LinesDataSet
from torch.utils.data import DataLoader
Proc_step=0
def step_excel():
    return Proc_step    
def test ( model,test_loader, acc_history, train_flag, acc_history_std , acc_history_median):
    model.eval()
    count =0
    acc_nean = []
    acc_std =[]
    acc_median =[]
    for indx, data in enumerate(test_loader):

        image1, image2, label = data
        image1 = image1.float().cuda()
        image2 = image2.float().cuda()
        image1 = image1[:,None,:,:]
        image2 = image2[:,None,:,:]
        label = label.cuda()
        with torch.no_grad():
            output = model(image1, image2)
            resultt= mean(output[:,0].cpu().numpy())[0]
            resultstd = std(output[:,0].cpu().numpy())
            result_median = median(output[:,0].cpu().numpy())
            _, predeict_= torch.max(output, dim=1, keepdim=False)
            acc_nean.append(resultt)
            acc_std.append(resultstd)
            acc_median.append(result_median)
            count+=1
        if count == 3:
            r = sum(acc_nean) /3  
            r_std =sum(acc_std)/3  
            r_median = sum(acc_median)/3    
            acc_history.append(r)
            acc_history_std.append(r_std)
            acc_history_median.append(r_median)
            count=0
            acc_nean = []
            acc_std =[]
            acc_median = []
    return acc_history , acc_history_std, acc_history_median

def creating_lines_for_each_file(path='data1_as_one_page',path_1="data_for_each_person"):
    
    if os.path.exists(path):

        print('Finding lines for each person...')

        files = os.listdir(path)

        if not os.path.exists(path_1):
            os.mkdir(path_1)
        for file in files:
            if file != '.DS_Store':
                number = file.split('.')[0]
                dir_name = 'person_{}'.format(number)
                if not os.path.exists(os.path.join(path_1, dir_name)):
                    os.mkdir(path_1 + '/' + dir_name)
                img = cv2.imread(path + '/' + file, 0)
                lines = detection_function.detect_lines(img)
                for indx, line in enumerate(lines):
                    to_save = Image.fromarray(line)
                    name = file.split('-')[1][0]
                    name = 'p'+str(number) + "_L_"+str((indx + 1))
                    to_save.save('{}/{}/{}.jpeg'.format(path_1,
                                                        dir_name, name))
        print('Done.')

def find_miss_match_pairs_two_writer(path='Motaz_for_each_Person',person1 = 1, person2 = 2 ):
    
    if os.path.exists(path):

        print('Creating all pairs of lines that creat a Miss Match and store the labels in csv file...')
        diff_data = []
        dir_name = path
        dirs = os.listdir(dir_name)
        person1_dir = "person_{}".format(person1)
        person2_dir = "person_{}".format(person2)
        file_person1 = []
        file_person2 = []
        for i in range (0 ,12):
                row1=random.randint(1,30)
                row2=random.randint(1,30)
                file_name  = "p{}_L_{}.jpeg".format(person1,row1)
                file_name1 = "p{}_L_{}.jpeg".format(person2,row2)
                file_to_search  = path +'/'+ person1_dir + '/' + file_name
                file_to_search1 = path +'/'+ person2_dir + '/' + file_name1
                while(os.path.exists(file_to_search) == False):
                    row1=random.randint(1,30)
                    file_name  = "p{}_L_{}.jpeg".format(person1,row1)
                    file_to_search = path +'/'+ person1_dir + '/' + file_name
                while(os.path.exists(file_to_search1) == False):
                    row2=random.randint(1,30)
                    file_name1 = "p{}_L_{}.jpeg".format(person2,row2)
                    file_to_search1 = path +'/'+ person2_dir + '/' + file_name1
                file_person1.append(file_name)
                file_person2.append(file_name1)
        for img1 in file_person1:
            for img2 in file_person2:
                to_add = []
                to_add.append(person1_dir + '/' + img1)
                to_add.append(person2_dir + '/' + img2)
                to_add.append('1')
                diff_data.append(to_add)
        csv_file = pd.DataFrame(diff_data)
        csv_file.to_csv("filename1.csv",index=False, sep=',', header=0)
        csv_file = csv_file.sample(frac=1)
        csv_file = csv_file[0:30] 
        print('Done.')
        return csv_file

def find_match_pairs_two_writer(path = "Motaz_for_each_Person" , person =1, flag= False):
    if os.path.exists(path):
        print('Creating all possible pairs of lines that creat a Match and store the labels in csv file...')
        dir_name = path
        genuin_data = []
        dirs = os.listdir(dir_name)
        dirs_to_search= "person_{}".format(person)
        for _dir in dirs:
            if _dir != '.DS_Store':
                files = os.listdir(dir_name + '/' + _dir)
                file =[]
                if _dir == dirs_to_search:
                    linee_number = []
                    for i in range(0,12):
                        row = random.randint(1,30)
                        file_name = "p{}_L_{}.jpeg".format(person, row)
                        file_to_search = dir_name + '/' + _dir + '/' + file_name
                        while(os.path.exists(file_to_search) == False) and int(row) not in linee_number:
                            row=random.randint(1,30)
                            file_name = "p{}_L_{}.jpeg".format(person, row)
                            file_to_search= dir_name + '/' + _dir + '/' + file_name
                        file.append(file_name)
                        linee_number.append(row)
                    for indx, img1 in enumerate(file):
                        for img2 in file[indx:]:
                            to_add = []
                            if img1 != img2:
                                to_add.append(_dir + '/' + img1)
                                to_add.append(_dir + '/' + img2)
                                to_add.append('0')
                                genuin_data.append(to_add)
        csv_file = pd.DataFrame(genuin_data)
        csv_file = csv_file.sample(frac=1)
        if flag == 1:
            csv_file = csv_file[0:31]
        else:
            csv_file = csv_file[0:30]




        return csv_file

def detect_lines(Excel_file,datapath):
    prepare_data.from_two_pages_to_jpeg(datapath,"Motaz_as_one_page")
    creating_lines_for_each_file("Motaz_as_one_page","Motaz_for_each_Person")
    prepare_data.Delete_White_Lines("Motaz_for_each_Person")
    prepare_data.resize_image("Motaz_for_each_Person")

def testing(filename1):

    acc_history = []
    acc_history_std =[]
    acc_history_median =[]
    test_data_set = LinesDataSet(filename1, 'Motaz_for_each_Person', transform=transforms.Compose([transforms.ToTensor()]))
    test_line_data_loader = DataLoader(test_data_set, shuffle=False, batch_size=10)
    model = Net()
    model = model.cuda()
    model.load_state_dict(torch.load('model_0.pt', map_location = 'cuda:0'))
    test(model, test_line_data_loader, acc_history=acc_history, acc_history_std= acc_history_std, train_flag=False, acc_history_median= acc_history_median)
    return acc_history , acc_history_std, acc_history_median

def looping_into_excel(Excel_file):
    excel_file=[]
    resultss= []
    csv_file = pd.DataFrame(excel_file)
    max_rows=Excel_file.shape[0]
    for i in range(max_rows):
        excel_file=[]
        toadd=[]
        #create data frame 
        csv_file = pd.DataFrame(excel_file)
        #take the first cell extract the name of the file
        first_file=Excel_file.loc[i][0]
        #take the second cell extract the name of the file
        second_file=Excel_file.loc[i][1]
        print(first_file + "," + second_file)
        global Proc_step
        Proc_step = (i+1)/max_rows       
        first_file_number = first_file.split(".")[0]
        second_file_number = second_file.split(".")[0]
        #name file excel
        filename1 = "match_Label.csv"
        #find match pairs for the first person
        first_csv = find_match_pairs_two_writer(person = first_file_number,flag=True)
        #find match pairs for the second person
        second_csv = find_match_pairs_two_writer(person = second_file_number)
        #concat the result to excel file
        csv_file = pd.concat([csv_file,first_csv])
        third_csv =  find_miss_match_pairs_two_writer( person1=first_file_number, person2=second_file_number)
        csv_file = pd.concat([csv_file,third_csv])
        csv_file = pd.concat([csv_file,second_csv])
        csv_file.to_csv(filename1,index=False, sep=',', header=0)
        print("Start testing")
        results , result_std , result_median= testing(filename1=filename1)
        toadd.append(first_file)
        toadd.append(second_file)

        toadd.append(results[0])
        toadd.append(result_std[0])
        toadd.append(result_median[0])

        toadd.append(results[1])
        toadd.append(result_std[1])
        toadd.append(result_median[1])

        toadd.append(results[2])
        toadd.append(result_std[2])
        toadd.append(result_median[2])

        resultss.append(toadd)
    main_Excel = pd.DataFrame(resultss)
    headerr= ["first","second","pfirst","pfirst_std","pfirst_median","pfs","pfs_std","pfs_median","psecond","psecond_std","psecond_median" ]
    main_Excel.to_csv("final1.csv",index=False,sep=",",header=headerr)
    return "final1.csv";



def testing_excel(excel_path, data_path):
   
    print("Starting reading excel file")
    test_file = pd.read_excel(excel_path)
    detect_lines(test_file,data_path)
    excel =looping_into_excel(test_file)
    return excel

testing_excel(r"Motaz.xlsx",r"C:\Users\97258\Desktop\Motaz")
