from app.search.search_manage import SearchManager

'''
Advanced interactive ACI that may be used in reproduction/verification
'''
class ReproductionACI:
    '''
    Search manager is required for updating the search indices
    '''
    def __init__(self, project_path: str, search_manager: SearchManager):
        self.project_path = project_path
        self.search_manager = search_manager
    def test_action(self):
        return 'Test action done successfully'
