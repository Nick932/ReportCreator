


class BaseReportCreator():
    
    
    def check_url_response(self,  url):
        '''
        This function checks response
        of the url.
        '''
        import requests,  sys

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
        
        import requests
        
        if self.check_url_response(users) and self.check_url_response(tasks):
        
            self.json_users = requests.get(users).json()
            self.json_tasks = requests.get(tasks).json()
            print(self.json_users[0]['id'], '\n', self.json_tasks[0])
            
        else:
            print('Operation aborted.')
        print('continue..')
        
        # file <username>:
        
        # <name> <email> datetime.now()
        # <company_name>
        #
        # 'Завершённые задачи:
        # some task1
        # some task2
        # Оставшиеся задачи:
        # some task 3        


    def create_report_from_json(self):
        try:
            self._get_info_from_json(self.users_source, self.tasks_source)
        except Exception:
            pass
        

if __name__ == '__main__':
    example = BaseReportCreator('https://json.medrating.org/users', 'https://json.medrating.org/todos')
    example.create_report_from_json()
