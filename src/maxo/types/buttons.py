from maxo.types.button import Button
from maxo.types.callback_button import CallbackButton
from maxo.types.chat_button import ChatButton
from maxo.types.link_button import LinkButton
from maxo.types.message_button import MessageButton
from maxo.types.open_app_button import OpenAppButton
from maxo.types.request_contact_button import RequestContactButton
from maxo.types.request_geo_location_button import RequestGeoLocationButton

InlineButtons = (
    CallbackButton
    | LinkButton
    | RequestGeoLocationButton
    | RequestContactButton
    | OpenAppButton
    | MessageButton
    | ChatButton
    | Button
)
