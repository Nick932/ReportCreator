import requests
import os, sys
import datetime, time


class Report_files:
    
    def __init__(self, user_and_tasks_pairs : list, foldername : str, 
                filetype : str):
    
        self.list_of_user_and_tasks_pairs = user_and_tasks_pairs
        self.foldername = foldername
        self.filetype = filetype


    def _file_already_exists(self, filename):
        
        cwd = os.getcwd()+os.sep+self.foldername
        return filename in os.listdir(cwd)

    
    def _get_file_edited_datetime(self, name_of_file):
        
        filename = name_of_file
        directory = os.getcwd()+os.sep+self.foldername
        
        edit_time = os.path.getmtime(directory+os.sep+filename)
        rawdatetime = datetime.datetime.strptime(time.ctime(edit_time), "%a %b %d %H:%M:%S %Y")
        date_n_time = str(rawdatetime).split(' ')
        
        return date_n_time
    
    
    def _rename_old_file(self, filename, filetype):
        
        type_of_file = filetype
        name_of_file = filename
        edit_date_n_time = self._get_file_edited_datetime(filename+filetype)
        # v It's like: _2020-09-23T15:25
        filename_tail = '_'+edit_date_n_time[0]+'T'+edit_date_n_time[1][:-3]
        directory = os.getcwd()+os.sep+self.foldername+os.sep
        
        try:
            os.rename(directory+name_of_file+type_of_file, 
            directory+name_of_file+filename_tail+type_of_file)
        except PermissionError:
            raise PermissionError('You have no permissions to create folder in this directory:\n', directory)
        except Exception:
            print('Unhandled exception while trying to rename existing file:', sys.exc_info()[1])
            raise Exception


    def _sort_tasks_by_status(self, tasks_dicts : list):
        
        tasks = tasks_dicts
        
        if tasks:
            completed_tasks_list = []
            
            for task in tasks:
                if task.get('completed', '') == True:
                    completed_tasks_list.append(tasks.pop(tasks.index(task)))
                    
            return completed_tasks_list, tasks
        else:
            return None
    
    
    def _create_tasks_text(self, tasks_dicts : list,  first_string : str, key_with_text):
        
        text_key = key_with_text
        tasks_list = tasks_dicts
        fs = first_string
        
        text = fs
        
        tasks_text = ''
        
        for task in tasks_list:
            
            task_text = task.get(text_key, '')
            if task_text:
                if len(task_text)>50:
                    task_text = task_text[:50]+'...'+'\n'
                else:
                    task_text = task_text+'\n'
                tasks_text += task_text
        
        if tasks_text:
            text += tasks_text
        else:
            text+='Список пуст.\n'
        
        return text
        

    def _create_report_text(self, user_info : dict, tasks_dicts : list ):
        
        user = user_info
        tasks = tasks_dicts
        
        username = user.get('name', 'unnamed_user_id'+str(user['id']))
        email = user.get('email', 'e-mail not stated')
        
        try:
            company = user['company']
        except KeyError:
            company_name = 'Company not stated'
        else:
            company_name = company['name']
        
        results = self._sort_tasks_by_status (tasks)
        if results:
            completed_tasks_list, other_tasks_list = results[0], results[1]
    
            text_of_all_completed_tasks = self._create_tasks_text(completed_tasks_list,
            'Завершённые задачи:\n', key_with_text = 'title')
            text_of_all_other_tasks = self._create_tasks_text( other_tasks_list, 
            'Остальные задачи:\n', key_with_text = 'title')
        else:
            text_of_all_completed_tasks = 'List is empty.'
            text_of_all_other_tasks = 'List is empty.'
        

        dt = datetime.datetime.today()
        date = str(dt.strftime('%d.%m.%Y'))
        time = str(dt.strftime('%H:%M'))
        
        report_text = '{0} <{1}> {2} {3}\n{4}\n\n{5}\n{6}'.format(username, 
        email, date, time, company_name, text_of_all_completed_tasks, text_of_all_other_tasks)
        return report_text
        

    def _create_report_file (self, filename : str, report_text : str):
        
        with open(self.foldername+os.sep+filename, 'w') as file:
            file.write(report_text)
            file.close()


    def create(self):
        
        for user_and_tasks in self.list_of_user_and_tasks_pairs:
            
            user, tasks = user_and_tasks[0],  user_and_tasks[1]
            report_text = self._create_report_text(user, tasks)
            
            filename = user.get('username', 'unnamed_user_id'+str(user['id']))

            if self._file_already_exists(filename+self.filetype):
                self._rename_old_file(filename, self.filetype)
                
            self._create_report_file(filename+self.filetype, report_text)
                


class Folder:
    
    def __init__(self, foldername : str):
        
        self.foldername = foldername
        
        if not isinstance(self.foldername, str):
            raise TypeError('Incorrect type of foldername: it must be str.')
            
    
    def _folder_already_exists(self, foldername, current_directory):
        
        cwd = current_directory
        
        # Create list of folders in current working directory.
        cwd_folders = [ object for object in os.listdir(cwd) if os.path.isdir(cwd+os.sep+object) ]
        
        return foldername in cwd_folders    
            
            
    def _create_folder(self, foldername,  current_directory):
        
        cwd = current_directory
        
        try:
            os.mkdir(cwd+os.sep+foldername)
        except PermissionError as exception:
            raise exception('You have no permissions to create folder in this directory:\n'+cwd)
        except Exception as exception:
            print('Some unhandled error has occured:\n', sys.exc_info()[1])
            raise exception
    
    
    def prepare(self):
        
        cwd = os.getcwd()
        if not self._folder_already_exists(self.foldername,  cwd):
            self._create_folder(self.foldername,  cwd)
        



class JSON_reporting:
    
    def __init__(self, users_source : str, tasks_source : str, foldername : str,
                filetype : str):
        
        self.foldername = foldername
        self.tasks_source = tasks_source
        self.users_source = users_source
        self.filetype = filetype
        
        if not isinstance(self.users_source, str):
            raise TypeError('Incorrect type of users_source: it must be str.')
            
        if not isinstance(self.tasks_source, str):
            raise TypeError('Incorrect type of tasks_source: it must be str.')
            
        if not isinstance(self.foldername, str):
            raise TypeError('Incorrect type of folder name: it must be str.')
        
        
    def _extract_data(self, JSON_source: str):
        
        JSON_adress = JSON_source
        
        try:
            response = requests.get(JSON_adress)
        except requests.exceptions.ConnectionError as exception:
            print('Error in '+str(self.__class__)+' while trying to connect:\n'+JSON_adress)
            raise exception
        else:
            list_with_info = response.json()
            return list_with_info


    def _group_up_user_tasks(self, users : list, tasks : list):
        ''' 
        Expected lists of dicts.
        
        Returns list of tuples, where:
        first element is dict of user's data,
        secont element is list of dicts of user's tasks data, or None.
        '''
        list_of_users = users
        list_of_tasks = tasks
        
        if not list_of_users:
            raise Exception('Error in '+str(self.__class__)+':\nThere are no users!')
        
        user_and_tasks_pairs = []
        
        for user in list_of_users:
            # create list of user's tasks (dict of task with it's info), on the way deleting user's task from general list_of_tasks.
            user_tasks = [list_of_tasks.pop(list_of_tasks.index(task)) for task in list_of_tasks if task.get('userId', '') == user['id']]
            user_and_tasks_pairs.append((user, user_tasks or None))
            
        return user_and_tasks_pairs
            
            
        
        


    def prepare(self):
        
        tasks_list = self._extract_data(self.tasks_source)
        users_list = self._extract_data(self.users_source)
        user_and_tasks_pairs = self._group_up_user_tasks (users = users_list, tasks = tasks_list)
        folder = Folder(self.foldername)
        folder.prepare()
        report_files = Report_files(user_and_tasks_pairs, self.foldername, self.filetype)
        report_files.create()
        
        

if __name__ == '__main__':
    reports = JSON_reporting ( users_source = 'https://json.medrating.org/users', 
    tasks_source = 'https://json.medrating.org/todos', foldername = 'tasks', filetype = '.txt')
    reports.prepare()
