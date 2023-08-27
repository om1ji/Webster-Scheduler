from pyrogram_patch.fsm import StatesGroup, StateItem

class Parameters(StatesGroup):
    has_no_schedule = StateItem()
    updating_schedule = StateItem()
    has_schedule = StateItem()
    has_no_qr = StateItem()
    updating_qr = StateItem()