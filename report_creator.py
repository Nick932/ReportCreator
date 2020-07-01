'''
This module contains BaseReportCreator - base class for report creating.
By default this class creates reports using JSON sources of information.

This class also can be extended with your own methods: for example, to 
create reports from files or other internet protocols.

Instance of this class takes 2 arguments: source of users and source
of the given users tasks.

To use:

1) Run this script as main file, with already defined URLs
2) Import class by another program and define it's instance,
   pointed necessary URLs.



@author: Nickolay Oborin.
Copyright 2020 Nickolay Oborin. All rights reserved.
'''




import requests, os, sys,  datetime, time


class BaseReportCreator():
    '''
    Base class for report creation.
    Takes 2 positional arguments: source of users
    and source of tasks owned by this users.
    '''

    def __init__(self,  users,  tasks):       
        self.users_source = users
        self.tasks_source = tasks
    
    
    
    def check_url_response(self,  url):
        '''
        This function checks response
        of the url. If its like '2xx', returns True.
        Else returns None.
        '''

        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as exception:
            error_message = '\n\nConnection to: \n{0}\n  -  Failed. \nConnection error \
was occured:\n{1}\n\nProbably reasons: internet connection lost or wrong URL.\n'.format(url, sys.exc_info()[:2])
            print(help(exception))
            print(exception.__context__)
            return None
        collected_info = requests.get(url)    
        result = str(collected_info).split(' ')

        if int(result[1][1]) !=2:
            HTTP_message = 'request to:\n{0}\nreturns HTTP-code {1}.'.format(url, result[1][:-1])
            print(HTTP_message)
            return None
        else:
            return True  
    
    
    
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



    def _check_answer_in_cwd_folders(self, answer, cwd_folders):
        '''
        Checks if user pointed folder name, which already
        exists.
        Returns true if folder already exists.
        '''
        
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
        
        print('Folder "', foldername, '" already exists.\nWould you like \
to create report files into "', foldername, '" or create new\
folder?\nInput "y" or "Y" to create report files into existing folder, or input name of new folder to create.')

        while True:
            answer = input()
            if answer == 'y' or answer == 'Y':
                return 'yes'
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
                    if name != 'yes':
                        foldername = name
                        folder_created = self._if_mkdir_permitted(cwd, foldername)
                        attempt_to_create_folder = 1
                        return folder_created, foldername
                    if name == 'yes':
                        return True,  foldername


        if not attempt_to_create_folder:
            folder_created = self._if_mkdir_permitted(cwd, foldername)
            return folder_created,  foldername
        
        
        
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
                    tasks_of_user.append(task)                        
            except KeyError:
                pass 
        
        
        for each in tasks_of_user:
            all_tasks.remove(each)
        
        return tasks_of_user,  all_tasks  
    
    
    
    def _check_name_or_give_id(self, obj, key, type, limit = False):
        '''
        Checks if there are obj['key'] value.
        Returns it's value or 'unnamed_user_id<obj['id']>'.
        '''
        
        
        try:
            name = str(obj[str(key)])
        except KeyError:
            name = 'unnamed_'+str(type)+'_id'+str(obj['id'])
            
        else:
            #print('> IT WAS: ', len(name))
            if limit == True:
                if len(name)>50:
                    name = name[:50]+'...'+'\n'
                    #print(len(name)-5, ' < IT BECOME.')
                else:
                    name = name+'\n'
                    
                    
        return name

        
    
    def report_text_creator(self, user, tasks_of_user):
        '''
        Creates full report text in str format.
        Returns whole report text for the given user, including
        user's tasks.
        '''
        
        
        def _return_key_or_not_stated(obj, key, atrname):
            '''
            Check obj['key'] value. 
            If there are no such
            key, return '<atrname> : not stated'.
            Else return key's value.
            '''
            try:
                value = obj[str(key)]
            except KeyError:
                value = str(atrname)+': not stated'
            return value
        
        

        
        def _if_empty_list(default_string, string):
            '''
            Checks if string is equal to default_string.
            If it is, returns default_string+'Empty list.' .
            If not, returns None.
            '''
            if str(string) == str(default_string):
                result = str(string)+'Empty list.' 
                return result
            return None
            
            
        user = user
        tasks = tasks_of_user
        username = self._check_name_or_give_id(user, 'name', 'user')
        email = _return_key_or_not_stated(user, 'email', 'email')
        
        dt = datetime.datetime.today()
        date = str(dt.strftime('%d.%m.%Y'))
        time = str(dt.strftime('%H:%M'))
        
        try:
            corp = user['company']
        except KeyError:
            company = 'Компания не указана.'
        else:
            company = _return_key_or_not_stated(corp, 'name', 'Компания')
        
        
        full_c_t = [] # task objects, not only names (like in the list bellow)
        completed_tasks_list = []

        for each in tasks:
            try:
                if each['completed'] == True:
                    full_c_t.append(each)
                    name = self._check_name_or_give_id(each, 'title', 'task',  limit = True)
                    completed_tasks_list.append(name)
            except KeyError:
                pass
        
        for each in full_c_t:
            tasks.remove(each) # now in 'tasks ' there will be only noncompleted tasks.
        
        
        completed_tasks_text = 'Завершённые задачи:\n'
        for each in completed_tasks_list:
            completed_tasks_text = completed_tasks_text+each
        
        
        ctt = _if_empty_list('Завершённые задачи:\n', completed_tasks_text)
        if ctt:
            completed_tasks_text = ctt+'\n'           
            
        
        other_tasks_list = tasks
        other_tasks_text = 'Оставшиеся задачи:\n'
        for tsk in other_tasks_list:
            name = self._check_name_or_give_id(tsk, 'title', 'task', limit = True)
            other_tasks_text = other_tasks_text+name
            
        ott = _if_empty_list('Оставшиеся задачи:\n', other_tasks_text)
        if ott:
            other_tasks_text = ott

        
        report = '{0} <{1}> {2} {3}\
\n{4}\n\n\
{5}\n\
{6}'.format(username, email, date, time, company, completed_tasks_text, other_tasks_text)
        return report

    
    
    def _check_file_exists(self, foldername, filename):
        '''
        Returns true, if file 'filename' exists
        in folder cwd/'foldername'. False - if not.
        '''
        directory = os.getcwd()+os.sep+foldername
        return str(filename) in os.listdir(directory)
    
    
    
    def create_report_file(self, text, folder,  filename,  filename_tail):
        '''
        This method creates report file with given text.
        File will has name 'filename' and will be located in the
        folder. If it is necessary, file will be renamed by adding
        filename_tail in the end of file name.
        Returns True, if file created, False - if not.
        '''
        directory = folder+os.sep
        oldname = filename
        
        if filename_tail:
            
            new_name = str(oldname)+str(filename_tail)
            
            try:
                os.rename(directory+oldname, directory+new_name)
            except PermissionError:
                print('You have no permissions to create folder in this directory:\n', directory)
                return False
            except Exception:
                print('Unhandled exception while trying to rename existing file:', sys.exc_info()[:2])
                return False
            else:
                with open(directory+oldname, 'w') as file:
                    file.write(text)
                return True
                
        else:
            with open(directory+oldname, 'w') as file:
                file.write(text)
            return True
        
        
    
    def create_report_from_json(self,  foldername='tasks'):
        '''
        Delegate all processes of report creation (using JSON source) to
        other class methods. Takes one argument: necessary folder name.
        '''
        
        self.json_users,  self.json_tasks = self._get_info_from_json(self.users_source, self.tasks_source)
        folder_created, new_foldername = self._create_folder(foldername)
        if new_foldername:
            foldername = new_foldername
        self._check_result_or_repeat(folder_created, self.create_report_from_json, foldername)        
        
        
        for user in self.json_users:
            
            tasks_of_user, self.json_tasks = self._filter_tasks_of_user(user,  self.json_tasks)
            report = self.report_text_creator(user, tasks_of_user)
            filename = self._check_name_or_give_id(user, 'username', 'user')
            filename_tail = None
            directory = os.getcwd()+os.sep+foldername
            
            if self._check_file_exists(foldername, filename):
                edit_time = os.path.getmtime(directory+os.sep+filename)
                rawdatetime = datetime.datetime.strptime(time.ctime(edit_time), "%a %b %d %H:%M:%S %Y")
                date_n_time = str(rawdatetime).split(' ')
                filename_tail = '_'+date_n_time[0]+'T'+date_n_time[1][:-3]
                
            report_created = self.create_report_file(report, directory, filename,  filename_tail)
            self._check_result_or_repeat(report_created, self.create_report_file,
            report, directory, filename, filename_tail)


                
if __name__ == '__main__':
    example = BaseReportCreator('https://json.medrating.org/users', 'https://json.medrating.org/todos')
    example.create_report_from_json('tasks')
