from pyteal import *

class Bookmyshow:

    def approval_program(self):

        # Define your TEAL approval program here

        # For example:

        program = Return(Int(1))

        return program

    def clear_program(self):

        # Define your TEAL clear program here

        # For example:

        program = Return(Int(1))

        return program

if __name__ == "__main__":

    bms = Bookmyshow()

    approval_program = bms.approval_program()

    clear_program = bms.clear_program()

    # Mode.Application specifies that this is a smart contract

    compiled_approval = compileTeal(approval_program, Mode.Application, version=6)

    with open("Bookmyshow_approval.teal", "w") as teal:

        teal.write(compiled_approval)

    # Mode.Application specifies that this is a smart contract

    compiled_clear = compileTeal(clear_program, Mode.Application, version=6)

    with open("Bookmyshow_clear.teal", "w") as teal:

        teal.write(compiled_clear)

