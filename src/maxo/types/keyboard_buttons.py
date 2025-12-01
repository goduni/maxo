
from maxo.types.callback_keyboard_button import CallbackKeyboardButton
from maxo.types.link_keyboard_button import LinkKeyboardButton
from maxo.types.message_keyboard_button import MessageKeyboardButton
from maxo.types.open_app_keyboard_button import OpenAppKeyboardButton
from maxo.types.request_contact_keyboard_button import RequestContactKeyboardButton
from maxo.types.request_geo_location_button import RequestGeoLocationKeyboardButton

KeyboardButtons = (
    CallbackKeyboardButton
    | LinkKeyboardButton
    | RequestGeoLocationKeyboardButton
    | RequestContactKeyboardButton
    | OpenAppKeyboardButton
    | MessageKeyboardButton
)
