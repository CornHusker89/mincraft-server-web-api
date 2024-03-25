

import asyncio
import boto3
import traceback

import dotenv
env_path = dotenv.find_dotenv()
env_values = dotenv.dotenv_values(env_path)

# get enviroment variables
aws_access_key = env_values["AWS_ACCESS_KEY"]
aws_secret_key = env_values["AWS_SECRET_KEY"]
region_name = env_values["EC2_REGION_NAME"]
instance_id = env_values["EC2_INSTANCE_ID"]

server_executable_path = env_values["SERVER_EXECUTABLE_PATH"]
server_executable_directory = server_executable_path[:server_executable_path.rfind("/")]
server_executable_name = server_executable_path[server_executable_path.rfind("/")+1:]



next_command_list: list = []
full_command_list: list = []
get_next_output: bool = False
return_string = ""
return_string_list = []
return_ready = False # if the return string is ready to be read


def log(message: str):
    """Appends a message to the log.txt file"""
    with open("log.txt", "a") as file:
        file.write(message + "\n")

def error_log(message: str):
    """Appends a message to the error_log.txt file"""
    with open("error_log.txt", "a") as file:
        file.write(message + "\n")


async def server():
    global next_command_list, get_next_output, return_string, return_ready, full_command_list, return_string_list
    stdout = asyncio.subprocess.PIPE
    shell_script = await asyncio.create_subprocess_shell(f"cd {server_executable_directory}/; ./{server_executable_name}",
                                                        shell=True, stdout=stdout, stderr=stdout, stdin=asyncio.subprocess.PIPE)

    asyncio.create_task(execute_command(shell_script))

    message_number = 0
    while True:
        if message_number < 22: # on inital startup, it sends like 20 somthing lines
            await asyncio.sleep(0.02)
            message_number += 1
        else:
            await asyncio.sleep(0.1)
        data = await shell_script.stdout.readline()
        line = data.decode('ascii').rstrip()
        log(line)

        if get_next_output:
            return_string_list.append(line)
            if next_command_list == []:
                for i, line in enumerate(return_string_list):
                    return_string += f"{full_command_list[i]} - {line}\n"

                return_string = return_string[:-1] # remove the last newline
                return_ready = True
                get_next_output = False
                


async def execute_command(shell_script: asyncio.subprocess.Process):
    global next_command_list, get_next_output
    while True:
        await asyncio.sleep(0.1)
        if not next_command_list == []: # if there are commands to be executed
            get_next_output = True
            shell_script.stdin.write(next_command_list.pop(0).encode('ascii') + b"\n")
            await shell_script.stdin.drain()


# kill the server if there are no players online
async def player_check():
    failed_lask_check = False
    while True:
        await asyncio.sleep(300)
        print("testing player count")
        message = await send_command(["testfor @a"])
        if message.find("No targets matched selector") != -1:
            if failed_lask_check:
                print("shutting down server")

                # Create an EC2 client
                ec2 = boto3.client('ec2', region_name=region_name, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

                # Restart the EC2 instance
                ec2.stop_instances(InstanceIds=[instance_id])
            else:
                failed_lask_check = True



async def send_command(commands: list) -> str:
    """
    Executes the command on the minecraft server
    (Async)
    
    Parameters:
        command (str or list): the list of commands to be executed
    """
    global next_command_list, get_next_output, return_ready, return_string, full_command_list, return_string_list
    return_string_list = []
    return_string = ""
    next_command_list = next_command_list + commands
    full_command_list = next_command_list.copy()
    return_ready = False
    
    while True:
        await asyncio.sleep(0.1)
        if return_ready:
            log(return_string)
            return return_string
    














