import requests
import os, sys
import datetime, time


class Report_files:
    '''
    Conducts all work on creating report files. Uses '.create()' method
    to start.
    
    Takes 3 arguments:
    - user_and_tasks_pairs (in list format) - list of tuples, where
      first element is a dict with user's data and second one is a list
      with dicts of tasks' data.
    - foldername (in str format) - name of a necessary folder for 
      report files.
    - filetype (in str format) - name of a file format without dot. For
      example - 'txt'.
    '''
    
    def __init__(self, user_and_tasks_pairs : list, foldername : str, 
                filetype : str):
    
        self.list_of_user_and_tasks_pairs = user_and_tasks_pairs
        self.foldername = foldername
        self.filetype = filetype


    def _file_already_exists(self, filename : str):
        '''
        Checks if file with 'filename' already exists
        in the 'self.foldername' of current working directory.
        
        Takes 1 argument:
        - filename (in str format) - name of the file (including type)
          to check.
          
        Returns True, if exists, else False.
        '''
        
        cwd = os.getcwd()+os.sep+self.foldername
        return filename in os.listdir(cwd)

    
    def _get_file_edited_datetime(self, name_of_file : str):
        '''
        Checks date and time of file editing.
        
        Takes 1 argument:
        - name_of_file (in str format) - name of the file (including type)
          which will be checked in "current directory/self.foldername".
          
        Returns list with date and time like: ['2020-07-04', '09:48:57'] .
        '''
        
        filename = name_of_file
        directory = os.getcwd()+os.sep+self.foldername
        
        edit_time = os.path.getmtime(directory+os.sep+filename)
        rawdatetime = datetime.datetime.strptime(time.ctime(edit_time), "%a %b %d %H:%M:%S %Y")
        # date_n_time wil be like " ['2020-07-04', '09:48:57'] "
        date_n_time = str(rawdatetime).split(' ')
        
        return date_n_time
    
    
    def _rename_old_file(self, filename : str, filetype : str):
        '''
        Tries to rename exiting file using date and time returned by
        self._get_file_edited_datetime() method.
        New name will be like: "<exiting_name>_2020-09-23T15:25.<type_of_file>.
        
        Takes 2 arguments:
        - filename (in str format) - name of the file to rename.
        - filetype (in str format) - a filetype of the file to rename.
        '''
        
        type_of_file = filetype
        name_of_file = filename
        edit_date_n_time = self._get_file_edited_datetime(filename+filetype)
        # v It's like: _2020-09-23T15:25
        filename_tail = '_'+edit_date_n_time[0]+'T'+edit_date_n_time[1][:-3]
        directory = os.getcwd()+os.sep+self.foldername+os.sep
        
        try:
            os.rename(directory+name_of_file+type_of_file, 
            directory+name_of_file+filename_tail+'.'+type_of_file)
        except PermissionError:
            raise PermissionError('You have no permissions to create folder in this directory:\n', directory)
        except Exception:
            print('Unhandled exception while trying to rename existing file:', sys.exc_info()[1])
            raise Exception


    def _sort_tasks_by_status(self, tasks_dicts : list):
        '''
        Sorts tasks by status.
        
        Takes 1 argument:
        - tasks_dicts (in list format) - list of tasks' dicts with their
          data.
          
        Returns tuple (first element is a list of completed tasks, second
        element is a list of other tasks) or None (if there are no tasks).
        '''
        
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
        '''
        Extracts values from each dict(from it's key named 'key_with_text) 
        located in 'tasks_dicts'. Creates text from connected values: 
        each value ends with '\n'; if value's length >50, truncates it
        to 50 symbols and add '...' in the end (before '\n'). Adds 
        at the beginning of text first string with value 'first_string'.
        Example (in braces):
        (first_string
        value1
        first-50-symbols-of-value2...
        value3
        )
        
        Takes 3 arguments:
        - tasks_dicts (in list format) - expected list of dicts: each
          dict is a task with it's data.
        - first_string (in str format) - text which must be putted in 
          the first string.
        - key_with_text (in str format) - dicts' key, whose value contains
          necessary for extraction text.
          
        Returns text (in str format).
        '''
        
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
        '''
        Creates an entire report's text.
        
        Takes 2 arguments:
        - user_info (in dict format) - dict of user's data.
        - tasks_dicts_ (in list format) - list of dicts, each of which
          contains task's data.
          
        Returns text of report, necessary to be in a report file 
        (in str format).
        '''
        
        user = user_info
        tasks = tasks_dicts
        
        name = user.get('name', 'unnamed_user_id'+str(user['id']))
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
        
        report_text = '{0} <{1}> {2} {3}\n{4}\n\n{5}\n{6}'.format(name, 
        email, date, time, company_name, text_of_all_completed_tasks, text_of_all_other_tasks)
        return report_text
        

    def _create_report_file (self, filename : str, report_text : str):
        
        with open(self.foldername+os.sep+filename, 'w') as file:
            file.write(report_text)
            file.close()


    def create(self):
        '''
        Method which initialize all files creation process.
        
        Delegates next tasks to internal methods of class:
        1. Creates text for the report file.
        2. Checks if an old report exists. If yes, renames it.
        2. Creates the new report file with the report text inside of it.
        
        Uses class'es attribute 'list_of_user_and_tasks_pairs'.
        '''
        for user_and_tasks in self.list_of_user_and_tasks_pairs:
            
            user, tasks = user_and_tasks[0],  user_and_tasks[1]
            report_text = self._create_report_text(user, tasks)
            
            filename = user.get('username', 'unnamed_user_id'+str(user['id']))

            if self._file_already_exists(filename+self.filetype):
                self._rename_old_file(filename, self.filetype)
                
            self._create_report_file(filename+self.filetype, report_text)
                


class Folder:
    '''
    Preparing folder for taks' files.
    Creates folder if it doesn't exists.
    
    Takes 1 argument:
    - foldername (in str format) - name of necessary folder for
      tasks' files.
    '''
    
    def __init__(self, foldername : str):
        
        self.foldername = foldername
        
        if not isinstance(self.foldername, str):
            raise TypeError('Incorrect type of foldername: it must be str.')
            
    
    def _folder_already_exists(self, foldername : str, current_directory : str):
        '''
        Checks if folder with such name already exists in the
        directory with executed file.
        
        Takes 2 arguments:
        - foldername (in str format) - name of necessary folder for
          tasks' files;
        - current_directory (in str format) - path to the current working
          directory.
          
        Returns True or False.
        '''
        
        cwd = current_directory
        
        # Create list of folders in current working directory.
        cwd_folders = [ object for object in os.listdir(cwd) if os.path.isdir(cwd+os.sep+object) ]
        
        return foldername in cwd_folders    
            
            
    def _create_folder(self, foldername : str,  current_directory : str):
        '''
        Creates a folder in the given directory.
        
        Takes 2 arguments:
        - foldername (in str format) - name of necessary folder;
        - current_directory (in str format) - necessary directory
          for the folder.
       ''' 
        
        cwd = current_directory
        
        try:
            os.mkdir(cwd+os.sep+foldername)
        except PermissionError as exception:
            raise exception('You have no permissions to create folder in this directory:\n'+cwd)
        except Exception as exception:
            print('Some unhandled error has occured:\n', sys.exc_info()[1])
            raise exception
    
    
    def prepare(self):
        '''
        Checks if the folder already exists. If not, creates it.
        Delegates both of these processes to internal methods.
        
        Defines current working directory for passing it to
        these internal methods like argument.
        '''
        cwd = os.getcwd()
        if not self._folder_already_exists(self.foldername,  cwd):
            self._create_folder(self.foldername,  cwd)
        



class JSON_reporting:
    
    '''
    Implements a decomposition pattern.
    
    Takes 4 arguments:
    - users_source (in str format) - expected URI for JSON-response;
    - tasks_source (in str format ) - expected URI for JSON-response;
    - foldername (in str format) - expected name of folder for reports' files;
    - filetype (in str format) - expected type of file without dot. By
      default,uses 'txt' type.
    '''
    def __init__(self, users_source : str, tasks_source : str, foldername : str,
                filetype : str):
        
        self.foldername = foldername
        self.tasks_source = tasks_source
        self.users_source = users_source
        if filetype:
            self.filetype = '.'+filetype
        else:
            self.filetype = '.txt'
        
        if not isinstance(self.users_source, str):
            raise TypeError('Incorrect type of users_source: it must be str.')
            
        if not isinstance(self.tasks_source, str):
            raise TypeError('Incorrect type of tasks_source: it must be str.')
            
        if not isinstance(self.foldername, str):
            raise TypeError('Incorrect type of folder name: it must be str.')
        
        
    def _extract_data(self, JSON_source: str):
        
        '''
        Takes 1 argument:
        - JSON_source (in str format) - expected URI for JSON data.
        
        Extracting data from JSON source. Checks connection errors.
        
        Returns JSON data (expected list of dicts).
        '''
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
        Takes 2 arguments:
        users (in list format) - expected list of users' data dicts.
        tasks (in list format) - expected list of tasks' data dicts.
        
        Group up tasks for each user.
        
        Returns list of tuples, where:
        first element of tuple is dict of user's data,
        secont element of tuple is list of dicts 
        of user's tasks data or None.
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
        
        '''
        Delegates next tasks to self methods:
        - Extracts data of users and tasks from JSON sources;
        - Group up tasks for each user;
        
        Delegates next tasks to other classes:
        - Preparing folder for tasks' files;
        - Creating report files;
        '''
        
        tasks_list = self._extract_data(self.tasks_source)
        users_list = self._extract_data(self.users_source)
        user_and_tasks_pairs = self._group_up_user_tasks (users = users_list, tasks = tasks_list)
        folder = Folder(self.foldername)
        folder.prepare()
        report_files = Report_files(user_and_tasks_pairs, self.foldername, self.filetype)
        report_files.create()
        
        

if __name__ == '__main__':
    reports = JSON_reporting ( users_source = 'https://json.medrating.org/users', 
    tasks_source = 'https://json.medrating.org/todos', foldername = 'tasks', filetype = 'txt')
    reports.prepare()
