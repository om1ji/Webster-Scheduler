from pyrogram_patch.fsm import StatesGroup, StateItem

class Parameters(StatesGroup):
    has_no_schedule = StateItem()
    updating_schedule = StateItem()