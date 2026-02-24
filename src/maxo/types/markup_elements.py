from maxo.types.emphasized_markup import EmphasizedMarkup
from maxo.types.link_markup import LinkMarkup
from maxo.types.monospaced_markup import MonospacedMarkup
from maxo.types.strikethrough_markup import StrikethroughMarkup
from maxo.types.strong_markup import StrongMarkup
from maxo.types.underline_markup import UnderlineMarkup
from maxo.types.user_mention_markup import UserMentionMarkup

MarkupElements = (
    EmphasizedMarkup
    | LinkMarkup
    | MonospacedMarkup
    | StrikethroughMarkup
    | StrongMarkup
    | UnderlineMarkup
    | UserMentionMarkup
)
