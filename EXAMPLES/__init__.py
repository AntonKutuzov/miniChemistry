from dataclasses import dataclass
from pathlib import Path
from time import sleep


# SETTINGS
@dataclass
class SETTINGS:
    SHOW_EXECUTION_TIME: bool = True
    READ_TIME: float = 1 # seconds


class EXAMPLE_LIST:
    EXAMPLE_1: str = 'Ex1_Find_product_mass'
    EXAMPLE_2: str = 'Ex2_Excess_and_limiting_reagent'


initial_message = """
The code in the examples is run slowly on purpose. The code is commented
well with explanations on what is done and by which function. To make it
possible to read by the user, the code execution is delayed. The variable
'READ_TIME' in 'SETTINGS' gives time in seconds that each message "sleeps"
before the code is ran further.

To disable or change the time, run the following code in the console:
>>> from EXAMPLES import SETTINGS
>>> SETTINGS.READ_TIME = 1
Or any other number. 0 to disable sleeping.

To run any example, use
>>> from EXAMPLES import run_example, EXAMPLE_LIST
>>> run_example(EXAMPLE_LIST.EXAMPLE_X)
With 'X' being the number of the example you want to run.
"""


def comment(*texts, sep=' ', end='\n',
            no_delay: bool = False,
            custom_delay: float = 0,
            approval: str = '',
            ) -> None:

    print(*texts, sep=sep, end=end)

    if approval:
        input(approval)
    elif custom_delay > 0 and SETTINGS.READ_TIME > 0:
        sleep(custom_delay)
    elif not no_delay:
        sleep(SETTINGS.READ_TIME)


def run_example(
                    file_name: str,
                    enter_after_doc: bool = True
                ) -> None:

    file = Path(__file__).parent / f'_Code/{file_name}.py'
    example_number = file_name.strip('Ex').split('_')[0]
    if not file.exists():
        raise Exception()

    code = file.read_text()
    doc = code.strip('"""').split('"""')[0]

    comment('The following exercise is solved in this example:\n', doc, '\n', no_delay=True)

    if enter_after_doc:
        input('Press "Enter" to continue >>> ')
    print(f'\n----- ====== RUNNING EXAMPLE {example_number} ====== ------')
    exec(code)
    print('\n----- ====== Done running the example code. ====== ------')


comment(
    initial_message,
    approval='Understood (press "Enter") >>>',
    end=' '
)
print('Choose an example and use the `run_example` function to properly run its code.\n\n')
