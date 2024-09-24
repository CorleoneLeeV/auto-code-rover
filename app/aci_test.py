from app.api.manage import ProjectApiManager
from app.data_structures import FunctionCallIntent, MessageThread
from app.task import Task
from app import utils as apputils


def aci_test(python_task: Task, task_output_dir: str):
    apputils.create_dir_if_not_exists(task_output_dir)
    api_manager = ProjectApiManager(python_task, task_output_dir)
    
    try:
        print('Start ACI test')
        msg_thread = MessageThread()
        tool_output, _, _ = api_manager.dispatch_intent(FunctionCallIntent('test_action', {}, None), msg_thread)
        print(tool_output)
        
    finally:
        python_task.reset_project()
