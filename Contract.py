from pyteal import *

class Bookmyshow:

    class Variables:

        name = Bytes("NAME")

        image = Bytes("IMAGE")

        description = Bytes("DESCRIPTION")

        price = Bytes("PRICE")

        sold = Bytes("SOLD")

        available_seats = Bytes("AVAILABLE_SEATS")

        event_date = Bytes("EVENT_DATE")

        event_time = Bytes("EVENT_TIME")

        location = Bytes("LOCATION")

        organizer = Bytes("ORGANIZER")

    class AppMethods:

        buy_ticket = Bytes("buy_ticket")
        get_product_info = Bytes("get_product_info")
	
	
    def application_creation(self):

        return Seq([

            Assert(Txn.application_args.length() == Int(10)),

            Assert(Txn.note() == Bytes("bookmyshow:uv1")),

            Assert(Btoi(Txn.application_args[3]) > Int(0)),

            Assert(Btoi(Txn.application_args[6]) > Int(0)),

            App.globalPut(self.Variables.name, Txn.application_args[0]),

            App.globalPut(self.Variables.image, Txn.application_args[1]),

            App.globalPut(self.Variables.description, Txn.application_args[2]),

            App.globalPut(self.Variables.price, Btoi(Txn.application_args[3])),

            App.globalPut(self.Variables.sold, Int(0)),

            App.globalPut(self.Variables.available_seats, Btoi(Txn.application_args[6])),

            App.globalPut(self.Variables.event_date, Txn.application_args[7]),

            App.globalPut(self.Variables.event_time, Txn.application_args[8]),

            App.globalPut(self.Variables.location, Txn.application_args[9]),

            App.globalPut(self.Variables.organizer, Txn.sender()),

            Approve()

        ])

    def buy_ticket(self):

    count = Txn.application_args[1]

    valid_number_of_transactions = Global.group_size() == Int(2)

    valid_payment_to_seller = And(

        Gtxn[1].type_enum() == TxnType.Payment,

        Gtxn[1].receiver() == Global.creator_address(),

        Gtxn[1].amount() == App.globalGet(self.Variables.price) * Btoi(count),

        Gtxn[1].sender() == Gtxn[0].sender(),

    )

    available_seats = App.globalGet(self.Variables.available_seats)

    seats_requested = Btoi(count)

    valid_seats_available = available_seats >= seats_requested

    can_buy = And(valid_number_of_transactions,

                  valid_payment_to_seller,

                  valid_seats_available)

    update_state = Seq([

        App.globalPut(self.Variables.sold, App.globalGet(self.Variables.sold) + Btoi(count)),

        App.globalPut(self.Variables.available_seats, available_seats - seats_requested),

        Approve()

    ])

    return If(can_buy).Then(update_state).Else(Reject())

        
            
    def get_product_info(self):

        return Seq([

            App.localPut(Int(0), self.Variables.name, App.globalGet(self.Variables.name)),

            App.localPut(Int(0), self.Variables.image, App.globalGet(self.Variables.image)),

            App.localPut(Int(0), self.Variables.description, App.globalGet(self.Variables.description)),

            App.localPut(Int(0), self.Variables.price, App.globalGet(self.Variables.price)),

            App.localPut(Int(0), self.Variables.sold, App.globalGet(self.Variables.sold)),

            App.localPut(Int(0), self.Variables.available_seats, App.globalGet(self.Variables.available_seats)),

            App.localPut(Int(0), self.Variables.event_date, App.globalGet(self.Variables.event_date)),

            App.localPut(Int(0), self.Variables.event_location, App.globalGet(self.Variables.event_location)),

                 Approve()

          ])
def add_show(self):

    return Seq([

        Assert(Txn.application_args.length() == Int(5)),

        Assert(Txn.note() == Bytes("bookmyshow-marketplace:uv1")),

        App.globalPut(self.Variables.name, Txn.application_args[0]),

        App.globalPut(self.Variables.image, Txn.application_args[1]),

        App.globalPut(self.Variables.description, Txn.application_args[2]),

        App.globalPut(self.Variables.price, Btoi(Txn.application_args[3])),

        App.globalPut(self.Variables.available_seats, Btoi(Txn.application_args[4])),

        Approve()

    ])
def update_show_details(self):

        show_id = Btoi(Txn.application_args[0])

        show_key = App.id() + Int(1) + show_id

        valid_conditions = And(

            Txn.sender() == App.globalGetEx(self.Variables.creator, show_key),

            Txn.application_args.length() == Int(5),

            Txn.time() < App.globalGetEx(self.Variables.show_time, show_key)

        )

        update_state = Seq([

            App.globalPutEx(show_key, self.Variables.show_name, Txn.application_args[1]),

            App.globalPutEx(show_key, self.Variables.show_venue, Txn.application_args[2]),

            App.globalPutEx(show_key, self.Variables.show_time, Btoi(Txn.application_args[3])),

            App.globalPutEx(show_key, self.Variables.ticket_price, Btoi(Txn.application_args[4])),

            Approve()

        ])

        return If(valid_conditions).Then(update_state).Else(Reject())

def cancel_booking(self):

        ticket_count = App.localGetEx(Int(0), App.localGet(Int(0), Txn.sender()))

        show_time = App.globalGet(self.Variables.show_time)

        valid_conditions = And(

            ticket_count > Int(0),

            Txn.application_args.length() == Int(0),

            Txn.time() < show_time

        )

        refund_amount = App.globalGet(self.Variables.ticket_price) * ticket_count

        update_state = Seq([

            App.globalPut(self.Variables.ticket_count, App.globalGet(self.Variables.ticket_count) + ticket_count),

            App.localPut(Int(0), App.localGet(Int(0), Txn.sender()), Int(0)),

            App.transfer(Txn.sender(), refund_amount),

            Approve()

        ])

        return If(valid_conditions).Then(update_state).Else(Reject())
			
			
def application_deletion(self):

    return Return(Txn.sender() == Global.creator_address())

def application_start(self):

    return Cond(

        [Txn.application_id() == Int(0), self.application_creation()],

        [Txn.on_completion() == OnComplete.DeleteApplication, self.application_deletion()],

        [Txn.application_args[0] == self.AppMethods.buy, self.buy_ticket()],

        [Txn.application_args[0] == self.AppMethods.show_info, self.get_product_info()],

        [Txn.application_args[0] == self.AppMethods.add_show, self.add_show()],

    )
def approval_program(self):

    return self.application_start()

def clear_program(self):

    return Return(Int(1))
			
			
			
