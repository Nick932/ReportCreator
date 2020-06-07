#TODO: 4.5 часа.
#WARNING: сделать проверку типа получаемых данных (словарь ли? Если из JSON)

import requests, os, sys


class BaseReportCreator():
    
    def check_url_response(self,  url):
        '''
        This function checks response
        of the url. If its like '2xx', returns True.
        Else returns None.
        '''

        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            error_message = '\n\nConnection to: \n{0}\n  -  Failed. \nConnection error \
was occured:\n{1}\n\nProbably reasons: internet connection lost or wrong URL.\n'.format(url, sys.exc_info()[:2])
            print(error_message)
            return None
        collected_info = requests.get(url)    
        result = str(collected_info).split(' ')

        if int(result[1][1]) !=2:
            HTTP_message = 'request to:\n{0}\nreturns HTTP-code {1}.'.format(url, result[1][:-1])
            print(HTTP_message)
            return None
        else:
            return True
            
    
    
    def __init__(self,  users,  tasks):       

        self.users_source = users
        self.tasks_source = tasks
    
    
    
    def _get_info_from_json (self, users, tasks):
        '''
        Getting info from JSON and returns it:
        first returned item is info from first given argument and so on.
        '''
        
        if self.check_url_response(users) and self.check_url_response(tasks):
        
            return requests.get(users).json(), requests.get(tasks).json()    
        else:
            print('Operation aborted.')
            sys.exit(1)
        
        
        
        # file <username>:
        
        # <name> <email> datetime.now()
        # <company_name>
        #
        # 'Завершённые задачи:
        # some task1
        # some task2
        # Оставшиеся задачи:
        # some task 3        


#____________________________________________________________________________

    def _check_answer_in_cwd_folders(self, answer, cwd_folders):
        if answer in cwd_folders:
            print('Folder with such name already exists. Try again.')
            return True
        else:
            return False
        


    def _choose_folder_name(self, foldername,  cwd_folders):
        '''
        This method checks if folder "foldername"
        already exists. If it is, asks user to create new
        name.
        Returns new name or none.
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
                if self._check_answer_in_cwd_folders(answer,  cwd_folders):
                    pass
                else:
                    return answer
                          
                          

    def _if_mkdir_permitted(self, cwd, foldername):
        '''
        Simple method which checks permission to create
        folder in current directory. If it's permitted,
        this method creates folder with name 'foldername'.
        Returns True if folder created. Else returns False.
        '''
        
        try:
            os.mkdir(cwd+os.sep+foldername)
        except PermissionError:
            print('You have no permissions to create folder in this directory:\n', cwd)
            return False
        except Exception:
            print('Some unhandled error has occured:\n', sys.exc_info()[:2])
            return False
        else:
            return True
            
            
            
    def _create_folder(self, foldername = 'tasks'):
        '''
        Checking if there already is folder with the given
        name. If it is, delegates name selection to the 
        '_choose_folder_name' method.
        Returns result of folder creation: True or False.
        '''
        cwd = os.getcwd()
        dir_content = os.listdir(cwd)
        attempt_to_create_folder = 0
        cwd_folders = []
        
        for element in dir_content:
            
            if os.path.isdir(cwd+os.sep+element):
                cwd_folders.append(element)
                
            if element == foldername:
                name = self._choose_folder_name(foldername,  cwd_folders)
                if name:
                    foldername = name
                    folder_created = self._if_mkdir_permitted(cwd, foldername)
                    attempt_to_create_folder = 1
                    return folder_created

        if not attempt_to_create_folder:
            folder_created = self._if_mkdir_permitted(cwd, foldername)
            return folder_created

#___________________________________________________________________________
        
        
    def _check_result_or_repeat(self, result, if_try_again, *args):
        '''
        This method checking result of the given expression('result'-arg.).
        If it's false, method starts the given function using
        given arguments.
        '''
        if not result:
            print('Would you like to try again now?\nInput "y" or "Y" if yes.')
            while True:
                answer = input()
                if answer == 'Y' or answer == 'y':
                    if_try_again(*args)
                else:
                    sys.exit(1)
        else:
            return
    
    
    
    def _filter_tasks_of_user(self, user, tasks):
        '''
        Filter tasks for only this one user.
        Returns tasks of this user and all tasks,
        excluding this user's own tasks.
        '''
        
        all_tasks = list(tasks)
        tasks_of_user = []

        for task in all_tasks:
            try:
                if task['userId']==user['id']:
                    # Переместить задачу из общего списка задач в список задач
                    # пользователя (с целью уменьшения кол-ва итераций 
                    # по списку ВСЕХ задач в дальнейшем).
                    tasks_of_user.append(all_tasks.pop(all_tasks.index(task)))                        
            except KeyError:
                pass 
        return tasks_of_user,  all_tasks  
    
    
    
    def create_report_from_json(self,  foldername='tasks'):
        
        self.json_users,  self.json_tasks = self._get_info_from_json(self.users_source, self.tasks_source)
        folder_created = self._create_folder(foldername)
        self._check_result_or_repeat(folder_created, self.create_report_from_json, foldername)        
        
        for user in self.json_users:
            tasks_of_user, self.json_tasks = self._filter_tasks_of_user(user,  self.json_tasks)
            #TODO: To be continued...
            report = report_creator(user, tasks_of_user)
            filename = _check_file_exists(user['username'])
            create_file(report, filename)
                
if __name__ == '__main__':
    example = BaseReportCreator('https://json.medrating.org/users', 'https://json.medrating.org/todos')
    example.create_report_from_json('tasks')
