


import os
import asyncio

server_executable_path = os.getenv("SERVER_EXECUTABLE_PATH")
server_executable_directory = server_executable_path[:server_executable_path.rfind("/")]
server_executable_name = server_executable_path[server_executable_path.rfind("/")+1:]

next_command_list: list = ["kill WAHuskeyFan"]

async def server():
    stdout = asyncio.subprocess.PIPE
    shell_script = await asyncio.create_subprocess_shell(f"cd {server_executable_directory}/; ./{server_executable_name}",
                                                        shell=True, stdout=stdout, stdin=asyncio.subprocess.PIPE)

    asyncio.create_task(execute_command(shell_script))

    while True:
        await asyncio.sleep(0.1)
        data = await shell_script.stdout.readline()
        line = data.decode('ascii').rstrip()
        print(line)


async def execute_command(shell_script: asyncio.subprocess.Process):
    global next_command_list
    while True:
        await asyncio.sleep(0.5)
        if not next_command_list == []: # if there are commands to be executed
            shell_script.stdin.write(next_command_list.pop(0).encode('ascii') + b"\n")
            await shell_script.stdin.drain()


def send_command(command: str) -> None:
    """
    Executes the command on the server
    """
    global next_command_list
    next_command_list.append(command)


loop = asyncio.get_event_loop()
loop.create_task(server())

if __name__ == "__main__":
    loop.run_forever()
    














