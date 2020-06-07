import os


def check_answer_in_cwd_folders(answer, cwd_folders):
    if answer in cwd_folders:
        print('Folder with such name already exists. Try again.')
        return True
    else:
        return False
    


def _choose_folder_name(foldername,  cwd_folders):
    '''
    This method checks if folder with "foldername"
    already exists. Returns necessary name of folder.
    '''
    
    print('Folder', foldername, 'already exists.\nWould you like \
to create report files into', foldername, 'or create new\
folder?\nInput "y" or "Y" for "yes"-anwser, or input name of new folder to create.')

    while True:
        answer = input()
        if answer == 'y' or answer == 'Y':
            return None
        if os.sep in answer:
            print("You can't use '/' symbol in the foldername! Try again.")
        else:
            if check_answer_in_cwd_folders(answer,  cwd_folders):
                pass
            else:
                return answer
                        


def _create_folder(foldername = 'tasks'):
    cwd = os.getcwd()
    dir_content = os.listdir(cwd)
    done = False
    cwd_folders = []
    for element in dir_content:
        print('1 step')
        if os.path.isdir(cwd+os.sep+element):
            print('1.1 step')
            print(element)
            cwd_folders.append(element)
        if element == foldername:
            print('2 step')
            name = _choose_folder_name(foldername,  cwd_folders)
            print('3 step')
            if name:
                print('4 step')
                foldername = name
                os.mkdir(cwd+os.sep+foldername)
                done = True
    print('5 step')
    if not done:
        os.mkdir(cwd+os.sep+foldername)

                        
    
_create_folder('example')
