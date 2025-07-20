from miniChemistry.Core.Reactions import HalfReaction
from miniChemistry.Core.Database.HalfReactionDatabase import HalfReactionDatabase
from typing import Optional, Dict
from miniChemistry.Core.CoreExceptions.stableExceptions import IonNotFound

# USE: Analytical chemistry formularium
# USE: LibreText Chemistry formularium
# THINK: maybe it makes sense to create a single class for all databases?


hrdb = HalfReactionDatabase()

SHORTCUTS: Dict[str, str] = {
    'H2O': 'w',
    'H(1)': 'h',
    'e(-1)': 'z'
}

def apply_shortcuts(command: str) -> str:
    for symbol, sc in SHORTCUTS.items():
        command = command.replace(sc, symbol)
    return command


command = ''
while True:
    if not command or not command[0] == '/':
        command = input(' >>> ')
    last_hr: Optional[HalfReaction] = None

    match command:
        case 'clear':
            print('This action will erase the whole half-reaction database.')
            confirmation1 = input('Are you sure you want to proceed? (Y/n): ')

            if confirmation1.lower() == 'y':
                confirmation2 = input('Type "confirm" to continue: ')
            else:
                continue

            if confirmation2 == 'confirm':
                hrdb._erase_database()
                print('The half-reaction database has been erased.')

        case 'remove'|'erase':
            if last_hr is not None:
                hrdb.remove_halfreaction(last_hr)
            else:
                print('No reaction can be removed from the database.')

        case 'read all'|'read':
            hrdb.print_df()

        case 'shortcuts':
            for symbol, sc in SHORTCUTS.items():
                print(f'{symbol} is encoded by "{sc}".')

        case 'exit':
            hrdb.save_dataframe()
            print('Previous reactions are saved.')
            break

        case ''|' ':
            continue

        case 'rewrite' | _:
            old_command = command

            if command == 'rewrite':
                command = input(' half-reaction scheme >>> ')

            command = apply_shortcuts(command)

            try:
                hr = HalfReaction.from_string(command)
            except IonNotFound as e:
                print('The ion used is not present in the database. Do it manually or add the ion.')
                print(e._message)
                continue
            except Exception as e:
                print('Failed to parse the reaction.')
                print(e)
                print('\nTry again.')
                continue

            potential = ''

            while not isinstance(potential, float):
                potential = input(' reaction potential >>> ')

                if potential == 'exit':
                    break

                try:
                    potential = float( potential )
                except Exception as e:
                    print('Could not read the potential value. Try again.')
                    print(e)

            if potential == 'exit':
                continue

            if not old_command == 'rewrite':
                try:
                    if not hrdb.halfreaction_present(hr):
                        hrdb.add_halfreaction(hr=hr, potential=potential)
                        last_hr = hr
                        print('The reaction is successfully saved.')
                    else:
                        print('The reaction is already present. Use rewrite().')
                except Exception as e:
                    hrdb.save_dataframe()
                    print('Failed to add the reaction to the database.')
                    print('Previous reaction are saved.')
                    print(e)
                    exit()
            else:
                try:
                    hrdb.rewrite_halfreaction(hr=hr, potential=potential)
                    print('Reaction is successfully rewritten.')
                except Exception as e:
                    # when you'll catch exact exceptions, if reaction is present, use 'continue'
                    hrdb.save_dataframe()
                    print('Could not rewrite the reaction.')
                    print('Previous reaction are saved.')
                    print(e)
                    exit()
